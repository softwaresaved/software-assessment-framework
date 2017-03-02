from flask import render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, SelectMultipleField
from app.main.forms import SoftwareSubmitForm, MultiCheckboxField
from app.models import db, Software, Score
from app import app
import hashlib
from plugins.repository.helper import *
import plugins.metric


# Routes and views

# Software Submission
@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    software_submit_form = SoftwareSubmitForm()
    failed = False
    # Is this a form submission?
    if software_submit_form.validate_on_submit():
        app.logger.info("Received a software submission: "+software_submit_form.url.data)

        # Examine the URL, locate a RepositoryHelper to use
        repos_helper = find_repository_helper(software_submit_form.url.data)
        if repos_helper is None:
            failed = True
            fail_message = "Sorry, we don't yet know how to talk to the repository at: " + software_submit_form.url.data
            app.logger.error("Unable to find a repository helper for: " + software_submit_form.url.data)
        else:
            # try to login
            try:
                repos_helper.login()
            except RepositoryHelperError as err:
                failed = True
                fail_message = err.message
                app.logger.error("Unable to log in to the repository, check URL and permissions?")

        if failed:
            flash(fail_message)
            return redirect(url_for('index'))
        else:
            # Create a new Software instance
            sw = Software(id=None,
                          name=software_submit_form.name.data,
                          description=software_submit_form.description.data,
                          version=software_submit_form.version.data,
                          submitter='User',
                          url=software_submit_form.url.data)
            # Persist it
            db.session.add(sw)
            db.session.commit()
            # Add to session
            session['sw_id'] = sw.id
            # Forward to metrics selection
            return redirect(url_for('metrics_interactive'))

    return render_template('index.html', form=software_submit_form)


# Non-interactive Metrics Selection
@app.route('/metrics/select/1', methods=['GET', 'POST'])
def metrics_interactive():
    # Load the software from the id stored in the session
    # NB - We use the software_id from the session, rather than from the request,
    # this prevents users other than the submitter changing the metrics to be run
    sw = Software.query.filter_by(id=session['sw_id']).first()
    # Load interactive metrics
    app.logger.info("Finding Interactive metrics")
    metrics = plugins.metric.load()

    # Construct the form
    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate it
    class InteractiveMetricRunForm(FlaskForm):
        pass

    for metric in metrics:
        if metric.INTERACTIVE:
            metric_key = hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest()
            setattr(InteractiveMetricRunForm, metric_key,
                    RadioField(label=metric.SHORT_DESCRIPTION, choices=metric.get_ui_choices().items()))

    setattr(InteractiveMetricRunForm, 'submit', SubmitField('Run Metrics'))
    # Get an instance
    interactive_metric_run_form = InteractiveMetricRunForm()

    # Deal with submission
    if interactive_metric_run_form.validate_on_submit():
        # Run the metrics
        run_interactive_metrics(interactive_metric_run_form.data, metrics, sw)

        # Forward to results display
        return redirect(url_for('metrics_automated', software_id=sw.id))

    return render_template('metrics_interactive.html', form=interactive_metric_run_form, software=sw)


# Automated Metrics Selection and Execution
@app.route('/metrics/select/2', methods=['GET', 'POST'])
def metrics_automated():
    # Load the software from the id stored in the session
    # NB - We use the software_id from the session, rather than from the request,
    # this prevents users other than the submitter changing the metrics to be run
    sw = Software.query.filter_by(id=session['sw_id']).first()

    # Load metrics
    app.logger.info("Finding automated metrics")
    metrics = plugins.metric.load()

    # Construct the form
    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate it
    class MetricRunForm(FlaskForm):
        pass
    metrics_availability = []
    metrics_usability = []
    metrics_maintainability = []
    metrics_portability = []

    for metric in metrics:
        if metric.INTERACTIVE:
            continue
        metric_key = hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest()
        if metric.CATEGORY == 'AVAILABILITY':
            metrics_availability.append((metric_key, metric.SHORT_DESCRIPTION))
        elif metric.CATEGORY == 'USABILITY':
            metrics_usability.append((metric_key, metric.SHORT_DESCRIPTION))
        elif metric.CATEGORY == 'MAINTAINABILITY':
            metrics_maintainability.append((metric_key, metric.SHORT_DESCRIPTION))
        elif metric.CATEGORY == 'PORTABILITY':
            metrics_portability.append((metric_key, metric.SHORT_DESCRIPTION))

    setattr(MetricRunForm, 'metrics_availability', MultiCheckboxField('Availability', choices=metrics_availability))
    setattr(MetricRunForm, 'metrics_usability', MultiCheckboxField('Usability', choices=metrics_usability))
    setattr(MetricRunForm, 'metrics_maintainability', MultiCheckboxField('Maintainability', choices=metrics_maintainability))
    setattr(MetricRunForm, 'metrics_portability', MultiCheckboxField('Portability', choices=metrics_portability))
    setattr(MetricRunForm, 'submit', SubmitField('Run Metrics'))

    metric_run_form = MetricRunForm()

    # Deal with submission
    if metric_run_form.validate_on_submit():
        # Load the RepositoryHelper again
        if sw.url and sw.url != "".strip():
            repos_helper = find_repository_helper(sw.url)
            repos_helper.login()

        # Run the appropriate metrics
        run_metrics(metric_run_form.metrics_usability.data, metrics, sw, repos_helper)
        run_metrics(metric_run_form.metrics_availability.data, metrics, sw, repos_helper)
        run_metrics(metric_run_form.metrics_maintainability.data, metrics, sw, repos_helper)
        run_metrics(metric_run_form.metrics_portability.data, metrics, sw, repos_helper)

        # Forward to results display
        return redirect(url_for('metrics_results', software_id=sw.id))

    return render_template('metrics_selection.html', form=metric_run_form, software=sw)


# Metrics results
@app.route('/metrics/results/<software_id>', methods=['GET'])
def metrics_results(software_id):
    # Load the Software
    sw = Software.query.filter_by(id=software_id).first()

    # Load the scores
    availability_scores = Score.query.filter_by(software_id=software_id, category="AVAILABILITY")
    usability_scores = Score.query.filter_by(software_id=software_id, category="USABILITY")
    maintainability_scores = Score.query.filter_by(software_id=software_id, category="MAINTAINABILITY")
    portability_scores = Score.query.filter_by(software_id=software_id, category="PORTABILITY")

    return render_template('metrics_results.html', software=sw, availability_scores=availability_scores, usability_scores=usability_scores, maintainability_scores=maintainability_scores, portability_scores=portability_scores)


def run_interactive_metrics(form_data, all_metrics, sw):
    """
    Match the selected boxes from the form submission to metrics and run.  Save the scores and feedback
    :param form_data: Metrics to run (List of md5 of the description)
    :param all_metrics: List of the available Metrics
    :param sw: The Software object being tested
    :return:
    """
    score_ids = []
    for metric_id, value in form_data.items():
        if metric_id == "submit" or metric_id == "csrf_token":
            continue
        for metric in all_metrics:
            if hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest() == metric_id:
                app.logger.info("Running metric: " + metric.SHORT_DESCRIPTION)
                metric.run(software=sw, form_data=value)
                app.logger.info(metric.get_score())
                app.logger.info(metric.get_feedback())
                score = Score(software_id=sw.id,
                              category=metric.CATEGORY,
                              short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION,
                              value=metric.get_score(),
                              feedback=metric.get_feedback())
                db.session.add(score)
                db.session.commit()
                score_ids.append(score.id)
    return score_ids


def run_metrics(form_data, metrics, sw, repos_helper):
    """
    Match the selected boxes from the form submission to metrics and run.  Save the scores and feedback
    :param form_data: Metrics to run (List of md5 of the description)
    :param metrics: List of the available Metrics
    :param sw: The Software object being tested
    :param repos_helper: A RepositoryHelper object
    :return:
    """
    score_ids = []
    for metric_id in form_data:
        for metric in metrics:
            if hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest() == metric_id:
                app.logger.info("Running metric: " + metric.SHORT_DESCRIPTION)
                metric.run(software=sw, helper=repos_helper)
                app.logger.info(metric.get_score())
                app.logger.info(metric.get_feedback())
                score = Score(software_id=sw.id,
                              category=metric.CATEGORY,
                              short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION,
                              value=metric.get_score(),
                              feedback=metric.get_feedback())
                db.session.add(score)
                db.session.commit()
                score_ids.append(score.id)
    return score_ids
