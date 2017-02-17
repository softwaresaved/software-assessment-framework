from flask import render_template, redirect, url_for, session
from app.main.forms import SoftwareSubmitForm, MultiCheckboxField
from flask_wtf import FlaskForm
from app.models import db, Software
from app import app
import hashlib
from wtforms import BooleanField, SubmitField, SelectMultipleField

import logging
import plugins.metric


# Routes and views

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


@app.route('/metrics_selection')
def metrics_selection():
    # ToDo Better classify metrics plugins and load 4 sets
    # Find / Iterate through metrics
    logging.info("Finding metrics")
    metrics = plugins.metric.load()

    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate

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

    if metricRunForm.validate_on_submit():

        # Run metrics
        # for metric in metrics:
        #     logging.info("Running metric: " + metric.get_short_description())
        #     metric.run(sw, repos_helper)
        #     logging.info(metric.get_score())
        #     logging.info(metric.get_feedback())
        # Forward to metrics selection

        #iterate through metrics and run

        return redirect(url_for('metrics_results'))

    return render_template('metrics_selection.html', form=metricRunForm)