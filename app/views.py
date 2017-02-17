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

    # Find / Iterate through metrics
    logging.info("Finding metrics")
    metrics = plugins.metric.load()

    # for metric in metrics:
    #     logging.info("Running metric: " + metric.get_short_description())
    #     metric.run(sw, repos_helper)
    #     logging.info(metric.get_score())
    #     logging.info(metric.get_feedback())

    # To dynamically add fields, we have to define the Form class at *runtime*, and instantiate

    class MetricRunform(FlaskForm):
        pass

    metrics_choices = []
    for metric in metrics:
        metric_key = hashlib.md5(metric.get_short_description().encode('utf-8')).hexdigest()
        metrics_choices.append((metric_key, metric.get_short_description()))

    setattr(MetricRunform, 'metrics_select', MultiCheckboxField('Select Metrics to run', choices = metrics_choices))
    setattr(MetricRunform, 'submit', SubmitField('Run Metrics'))

    metricRunForm = MetricRunform()
    return render_template('metrics_selection.html', form=metricRunForm)