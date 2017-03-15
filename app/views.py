from flask import render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, FormField, BooleanField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired
from app.main.forms import SoftwareSubmitForm
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
            # Forward to interactive (self-assessment) metrics selection
            return redirect(url_for('metrics_interactive'))

    return render_template('index.html', form=software_submit_form)


# Interactive Metrics Selection
@app.route('/metrics/select/interactive', methods=['GET', 'POST'])
def metrics_interactive():
    # Load the software from the id stored in the session
    # NB - We use the software_id from the session, rather than from the request,
    # this prevents users other than the submitter changing the metrics to be run
    sw = Software.query.filter_by(id=session['sw_id']).first()
    # Load interactive metrics
    app.logger.info("Finding Interactive metrics")
    # FixMe - implement a category based filter for plugin loading to avoid repetition below
    metrics = plugins.metric.load()

    # In order to be able to separate, and label the categories, we need to create *individual* sub-form classes
    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate it.
    # This feels *wrong* and *bad*, but it has to be done this way.
    class InteractiveMetricAvailabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class InteractiveMetricUsabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class InteractiveMetricMaintainabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class InteractiveMetricPortabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    # Add metrics to their appropriate sub-forms classes (not instances)
    # FixMe - Because the choices come from a dictionary, the sort order is random
    for metric in metrics:
        if metric.INTERACTIVE:
            metric_key = hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest()
            if metric.CATEGORY == "AVAILABILITY":
                setattr(InteractiveMetricAvailabilityForm, metric_key,
                        RadioField(label=metric.SHORT_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricAvailabilityForm, "IMPORTANCE_" + metric_key,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "USABILITY":
                setattr(InteractiveMetricUsabilityForm, metric_key,
                        RadioField(label=metric.SHORT_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricUsabilityForm, "IMPORTANCE_"+metric_key,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "MAINTAINABILITY":
                setattr(InteractiveMetricMaintainabilityForm, metric_key,
                        RadioField(label=metric.SHORT_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricMaintainabilityForm, "IMPORTANCE_" + metric_key,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "PORTABILITY":
                setattr(InteractiveMetricPortabilityForm, metric_key,
                        RadioField(label=metric.SHORT_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricPortabilityForm, "IMPORTANCE_" + metric_key,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

    # Build the top-level form with the instances of the now populated sub-form classes.
    class InteractiveMetricRunForm(FlaskForm):
        ff_a = FormField(InteractiveMetricAvailabilityForm, label="Availability", description="Can a user find the software (discovery) and can they obtain the software (access)?")
        ff_u = FormField(InteractiveMetricUsabilityForm, label="Usability", description="Can a user understand the operation of the software, such they can use it, integrate it with other software and extend or modify it?")
        ff_m = FormField(InteractiveMetricMaintainabilityForm, label="Maintainability", description="What is the likelihoood that the software can be maintained and developed over a period of time?")
        ff_p = FormField(InteractiveMetricPortabilityForm, label="Portability", description="What is the capacity for using the software in a different area, field or environment?")
        submit = SubmitField('Next')

    # Get an instance of the top leve form
    interactive_metric_run_form = InteractiveMetricRunForm()

    # Deal with submission
    if interactive_metric_run_form.validate_on_submit():
        # Run the metrics
        run_interactive_metrics(interactive_metric_run_form.ff_u.data, metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_a.data, metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_m.data, metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_p.data, metrics, sw)
        # Forward to automater metrics
        return redirect(url_for('metrics_automated'))

    # Default action

    flash_errors(interactive_metric_run_form)
    return render_template('metrics_select.html', page_title="Self Assessment",
                           form=interactive_metric_run_form,
                           form_target="metrics_interactive",
                           software=sw)


# Automated Metrics Selection and Execution
@app.route('/metrics/select/automated', methods=['GET', 'POST'])
def metrics_automated():
    # Load the software from the id stored in the session
    # NB - We use the software_id from the session, rather than from the request,
    # this prevents users other than the submitter changing the metrics to be run
    sw = Software.query.filter_by(id=session['sw_id']).first()
    # Load automated metrics
    app.logger.info("Finding automated metrics")
    metrics = plugins.metric.load()

    # In order to be able to separate, and label the categories, we need to create *individual* sub-form classes
    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate it.
    # This feels *wrong* and *bad*, but it has to be done this way.
    class AutoMetricAvailabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class AutoMetricUsabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class AutoMetricMaintainabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    class AutoMetricPortabilityForm(FlaskForm):
        importance = IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1})

    # Add metrics to their appropriate sub-forms classes (not instances)
    # FixMe - Because the choices come from a dictionary, the sort order is random
    for metric in metrics:
        if metric.INTERACTIVE:
            continue
        metric_key = hashlib.md5(metric.SHORT_DESCRIPTION.encode('utf-8')).hexdigest()
        if metric.CATEGORY == "AVAILABILITY":
            setattr(AutoMetricAvailabilityForm, metric_key,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricAvailabilityForm, "IMPORTANCE_" + metric_key,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "USABILITY":
            setattr(AutoMetricUsabilityForm, metric_key,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricUsabilityForm, "IMPORTANCE_" + metric_key,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "MAINTAINABILITY":
            setattr(AutoMetricMaintainabilityForm, metric_key,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricMaintainabilityForm, "IMPORTANCE_" + metric_key,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "PORTABILITY":
            setattr(AutoMetricPortabilityForm, metric_key,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricPortabilityForm, "IMPORTANCE_" + metric_key,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        # Build the top-level form with the instances of the now populated sub-form classes.
        class AutomatedMetricRunForm(FlaskForm):
            ff_a = FormField(AutoMetricAvailabilityForm, label="Availability",
                             description="Can a user find the software (discovery) and can they obtain the software (access)?")
            ff_u = FormField(AutoMetricUsabilityForm, label="Usability",
                             description="Can a user understand the operation of the software, such they can use it, integrate it with other software and extend or modify it?")
            ff_m = FormField(AutoMetricMaintainabilityForm, label="Maintainability",
                             description="What is the likelihoood that the software can be maintained and developed over a period of time?")
            ff_p = FormField(AutoMetricPortabilityForm, label="Portability",
                             description="What is the capacity for using the software in a different area, field or environment?")
            submit = SubmitField('Next')

        # Get an instance of the top leve form
        automated_metric_run_form = AutomatedMetricRunForm()

    # Deal with submission
    if automated_metric_run_form.validate_on_submit():
        # Load the RepositoryHelper again
        if sw.url and sw.url != "".strip():
            repos_helper = find_repository_helper(sw.url)
            repos_helper.login()

        # Run the appropriate metrics
        run_automated_metrics(automated_metric_run_form.ff_u.data, metrics, sw, repos_helper)
        run_automated_metrics(automated_metric_run_form.ff_a.data, metrics, sw, repos_helper)
        run_automated_metrics(automated_metric_run_form.ff_m.data, metrics, sw, repos_helper)
        run_automated_metrics(automated_metric_run_form.ff_p.data, metrics, sw, repos_helper)

        # Forward to results display
        return redirect(url_for('metrics_results', software_id=sw.id))

    flash_errors(automated_metric_run_form)
    return render_template('metrics_select.html', page_title="Automated Assessment",
                           form=automated_metric_run_form,
                           form_target="metrics_automated",
                           software=sw)


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

    return render_template('metrics_results.html',
                           software=sw,
                           scores={"Availability": availability_scores, "Usability": usability_scores,
                                   "Maintainability": maintainability_scores, "Portability": portability_scores}
                           )


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
                score = Score(software_id=sw.id, category=metric.CATEGORY, short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION, value=metric.get_score(),
                              feedback=metric.get_feedback(), category_importance=form_data['importance'],
                              metric_importance=form_data['IMPORTANCE_'+metric_id])
                db.session.add(score)
                db.session.commit()
                score_ids.append(score.id)
    return score_ids


def run_automated_metrics(form_data, metrics, sw, repos_helper):
    """
    Match the selected boxes from the form submission to metrics and run.
    Save the scores and feedback
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
                score = Score(software_id=sw.id, category=metric.CATEGORY, short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION, value=metric.get_score(),
                              feedback=metric.get_feedback())
                db.session.add(score)
                db.session.commit()
                score_ids.append(score.id)
    return score_ids


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Response required in %s " % (
                getattr(form, field).label.text
            ))