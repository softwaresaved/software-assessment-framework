from flask import render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectMultipleField
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
    softwareSubmitForm = SoftwareSubmitForm()
    if softwareSubmitForm.validate_on_submit():
        # Create a new Software instance
        sw = Software(id=None,
                      name=softwareSubmitForm.name.data,
                      description=softwareSubmitForm.description.data,
                      version=softwareSubmitForm.version.data,
                      submitter='User',
                      url=softwareSubmitForm.url.data)
        # Persist it
        db.session.add(sw)
        db.session.commit()
        # Add to session
        session['sw_id'] = sw.id
        # Forward to metrics selection
        return redirect(url_for('metrics_selection'))

    return render_template('index.html', form=softwareSubmitForm)

# Metrics Selection and Execution
@app.route('/metrics_selection', methods=['GET', 'POST'])
def metrics_selection():

    # Load metrics
    app.logger.info("Finding metrics")
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
        metric_key = hashlib.md5(metric.get_short_description().encode('utf-8')).hexdigest()
        if metric.category == 'AVAILABILITY':
            metrics_availability.append((metric_key, metric.get_short_description()))
        elif metric.category == 'USABILITY':
            metrics_usability.append((metric_key, metric.get_short_description()))
        elif metric.category == 'MAINTAINABILITY':
            metrics_maintainability.append((metric_key, metric.get_short_description()))
        elif metric.category == 'PORTABILITY':
            metrics_portability.append((metric_key, metric.get_short_description()))

    setattr(MetricRunForm, 'metrics_availability', MultiCheckboxField('Availability', choices=metrics_availability))
    setattr(MetricRunForm, 'metrics_usability', MultiCheckboxField('Usability', choices=metrics_usability))
    setattr(MetricRunForm, 'metrics_maintainability', MultiCheckboxField('Maintainability', choices=metrics_maintainability))
    setattr(MetricRunForm, 'metrics_portability', MultiCheckboxField('Portability', choices=metrics_portability))
    setattr(MetricRunForm, 'submit', SubmitField('Run Metrics'))

    metricRunForm = MetricRunForm()

    # Deal with submission
    if metricRunForm.validate_on_submit():

        # Load the software from the id stored in the session
        sw = Software.query.filter_by(id=session['sw_id']).first()
        # Examine the URL, identify which repository helper to use
        if sw.url and sw.url != "".strip():
            repos_helper = find_repository_helper(sw.url)
            if repos_helper is None:
                app.logger.error('Unable to process software item: ' + sw.name)
                flash('Unable to locate a repository helper for '+sw.url)
                return redirect(url_for('index'))

        # Run the appropriate metrics
        session['availability_score_ids'] = run_metrics(metricRunForm.metrics_availability.data, metrics, sw, repos_helper)
        session['usability_score_ids']= run_metrics(metricRunForm.metrics_usability.data, metrics, sw, repos_helper)
        session['maintainability_score_ids']= run_metrics(metricRunForm.metrics_maintainability.data, metrics, sw, repos_helper)
        session['portability_score_ids'] = run_metrics(metricRunForm.metrics_portability.data, metrics, sw, repos_helper)

        # FIXME - just save the software_id and load from there.

        # Forward to results display
        return redirect(url_for('metrics_results'))

    return render_template('metrics_selection.html', form=metricRunForm)

# Metrics results
@app.route('/metrics_results', methods=['GET'])
def metrics_results():
    availability_scores = load_scores(session['availability_score_ids'])
    usability_scores = load_scores(session['usability_score_ids'])
    maintainability_scores = load_scores(session['maintainability_score_ids'])
    portability_scores = load_scores(session['portability_score_ids'])

    return render_template('metrics_results.html', availability_scores=availability_scores, usability_scores=usability_scores, maintainability_scores=maintainability_scores, portability_scores=portability_scores)


def run_metrics(formData, metrics, sw, repos_helper):
    """
    Match the selected boxes from the form submission to metrics and run.  Save the scores and feedback
    :param formData: The selected metrics (md5 of the description)
    :param metrics: All the available metrics
    :return:
    """
    score_ids = []
    for m in formData:
        for metric in metrics:
            if hashlib.md5(metric.get_short_description().encode('utf-8')).hexdigest() == m:
                app.logger.info("Running metric: " + metric.get_short_description())
                metric.run(sw, repos_helper)
                app.logger.info(metric.get_score())
                app.logger.info(metric.get_feedback())
                score = Score(software_id=sw.id,
                              short_description=metric.get_short_description(),
                              long_description=metric.get_long_description(),
                              value=metric.get_score(),
                              feedback=metric.get_feedback())
                db.session.add(score)
                db.session.commit()
                score_ids.append(score.id)
    return score_ids


def load_scores(score_ids):
    scores = []
    for score_id in score_ids:
        scores.append(Score.query.filter_by(id=score_id).first())
    return scores


