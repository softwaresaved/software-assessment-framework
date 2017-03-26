from flask import render_template, redirect, url_for, session, flash, abort
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

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    """
    Index Page
    :return: 
    """
    return render_template('index.html')


@app.route('/software', methods=['GET'])
def browse_software():
    """
    Browse Software Submissions
    :return: 
    """
    sw_all = Software.query.group_by(Software.name, Software.version)
    return render_template('software.html', sw_all=sw_all)


@app.route('/metrics', methods=['GET'])
def browse_metrics():
    """
    List Metrics
    :return: 
    """
    all_metrics = plugins.metric.load()

    # Todo - move this all out to a separate module. Define metric categories and descriptions, loading and filtering

    metrics_availabilty = []
    metrics_usability = []
    metrics_maintainability = []
    metrics_portability = []
    for metric in all_metrics:
        if metric.CATEGORY == "AVAILABILITY":
            metrics_availabilty.append(metric)
        if metric.CATEGORY == "USABILITY":
            metrics_usability.append(metric)
        if metric.CATEGORY == "MAINTAINABILITY":
            metrics_maintainability.append(metric)
        if metric.CATEGORY == "PORTABILITY":
            metrics_portability.append(metric)

    a_meta = {"category_name": "Availability",
              "category_description": "Can a user find the software (discovery) and can they obtain the software (access)?",
              "metrics": metrics_availabilty}

    u_meta = {"category_name": "Usability",
              "category_description": "Can a user understand the operation of the software, such they can use it, integrate it with other software and extend or modify it?",
              "metrics": metrics_usability}

    m_meta = {"category_name": "Maintainability",
              "category_description": "What is the likelihoood that the software can be maintained and developed over a period of time?",
              "metrics": metrics_maintainability}

    p_meta = {"category_name": "Portability",
              "category_description": "What is the capacity for using the software in a different area, field or environment?",
              "metrics": metrics_portability}

    return render_template('metrics.html',
                           a_meta=a_meta,
                           u_meta=u_meta,
                           m_meta=m_meta,
                           p_meta=p_meta)


@app.route('/metrics/<metric_identifier>', methods=['GET'])
def show_metric(metric_identifier):
    """
    Display a single metric
    :param metric_identifier: 
    :return: 
    """
    the_metric = None
    metrics_all = plugins.metric.load()
    for m in metrics_all:
        if m.IDENTIFIER == metric_identifier:
            the_metric = m

    if the_metric is None:
        # We don't recognise that id
        abort(404)

    return render_template('metric.html', metric=the_metric)


@app.route('/submit', methods=['GET', 'POST'])
def submit_software():
    """
    Submire software for assessment
    :return: 
    """
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
            return redirect(url_for('submit'))
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

    return render_template('submit.html', form=software_submit_form)


@app.route('/submit/interactive', methods=['GET', 'POST'])
def metrics_interactive():
    """
    Interactive Metrics Selection
    :return: 
    """
    # Load the software from the id stored in the session
    # NB - We use the software_id from the session, rather than from the request,
    # this prevents users other than the submitter changing the metrics to be run
    sw = Software.query.filter_by(id=session['sw_id']).first()
    # Load interactive metrics
    app.logger.info("Finding Interactive metrics")
    # FixMe - implement a category based filter for plugin loading to avoid repetition below
    all_metrics = plugins.metric.load()

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
    for metric in all_metrics:
        if metric.SELF_ASSESSMENT:
            if metric.CATEGORY == "AVAILABILITY":
                setattr(InteractiveMetricAvailabilityForm, metric.IDENTIFIER,
                        RadioField(label=metric.LONG_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricAvailabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "USABILITY":
                setattr(InteractiveMetricUsabilityForm, metric.IDENTIFIER,
                        RadioField(label=metric.LONG_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricUsabilityForm, "IMPORTANCE_"+metric.IDENTIFIER,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "MAINTAINABILITY":
                setattr(InteractiveMetricMaintainabilityForm, metric.IDENTIFIER,
                        RadioField(label=metric.LONG_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricMaintainabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
                        IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))
            if metric.CATEGORY == "PORTABILITY":
                setattr(InteractiveMetricPortabilityForm, metric.IDENTIFIER,
                        RadioField(label=metric.LONG_DESCRIPTION, choices=metric.get_ui_choices().items(), validators=[DataRequired()]))
                setattr(InteractiveMetricPortabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
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
        run_interactive_metrics(interactive_metric_run_form.ff_u.data, all_metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_a.data, all_metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_m.data, all_metrics, sw)
        run_interactive_metrics(interactive_metric_run_form.ff_p.data, all_metrics, sw)
        # Forward to automater metrics
        return redirect(url_for('metrics_automated'))

    # Default action

    flash_errors(interactive_metric_run_form)
    return render_template('metrics_select.html', page_title="Self Assessment",
                           form=interactive_metric_run_form,
                           form_target="metrics_interactive",
                           preamble="Answer the following questions about your software, indicating their importance to you.",
                           software=sw)


@app.route('/submit/automated', methods=['GET', 'POST'])
def metrics_automated():
    """
    Automated Metrics Selection and Execution
    :return: 
    """
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
        if metric.SELF_ASSESSMENT:
            continue
        if metric.CATEGORY == "AVAILABILITY":
            setattr(AutoMetricAvailabilityForm, metric.IDENTIFIER,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricAvailabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "USABILITY":
            setattr(AutoMetricUsabilityForm, metric.IDENTIFIER,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricUsabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "MAINTAINABILITY":
            setattr(AutoMetricMaintainabilityForm, metric.IDENTIFIER,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricMaintainabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
                    IntegerRangeField("Importance to you:", render_kw={"value": 0, "min": 0, "max": 1}))

        if metric.CATEGORY == "PORTABILITY":
            setattr(AutoMetricPortabilityForm, metric.IDENTIFIER,
                    BooleanField(label=metric.SHORT_DESCRIPTION))
            setattr(AutoMetricPortabilityForm, "IMPORTANCE_" + metric.IDENTIFIER,
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

        # Get an instance of the top level form
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
        return redirect(url_for('metrics_scores', software_id=sw.id))

    flash_errors(automated_metric_run_form)
    return render_template('metrics_select.html', page_title="Automated Assessment",
                           form=automated_metric_run_form,
                           form_target="metrics_automated",
                           preamble="Select from the following automated metrics to run against your repository, indicating their importance to you.",
                           software=sw)


@app.route('/scores/<software_id>', methods=['GET'])
def metrics_scores(software_id):
    """
    Metrics scores (raw scores - post submission)
    :param software_id: 
    :return: 
    """
    # Load the Software
    sw = Software.query.filter_by(id=software_id).first()

    # Load the scores
    availability_scores = Score.query.filter_by(software_id=software_id, category="AVAILABILITY")
    usability_scores = Score.query.filter_by(software_id=software_id, category="USABILITY")
    maintainability_scores = Score.query.filter_by(software_id=software_id, category="MAINTAINABILITY")
    portability_scores = Score.query.filter_by(software_id=software_id, category="PORTABILITY")

    return render_template('metrics_scores.html',
                           software=sw,
                           scores={"Availability": availability_scores, "Usability": usability_scores,
                                   "Maintainability": maintainability_scores, "Portability": portability_scores}
                           )


@app.route('/awards/<software_id>', methods=['GET'])
def metrics_awards(software_id):
    """
    Calculate the awards, based on the scores
    :param software_id: 
    :return: 
    """
    # Load the Software
    sw = Software.query.filter_by(id=software_id).first()

    if sw is None:
        # We don't recognise that id
        abort(404)

    award = None
    if has_bronze_award(software_id):
        award = "Bronze"
        app.logger.info("Passed Bronze")
        if has_silver_award(software_id):
            award = "Silver"
            app.logger.info("Passed Silver")
    else:
        app.logger.info("Failed Bronze")

    # Find the most recent assessment
    assessment_date = Score.query.filter_by(software_id=software_id).order_by(Score.updated).first().updated

    return render_template('metrics_awards.html',
                           software=sw,
                           award=award,
                           assessment_date=assessment_date)


def has_bronze_award(software_id):
    """
    Ascertain if the piece of software had passed metrics to achieve a bronze award
    :param software_id:
    :return: True if passed, otherwise false
    """
    # FixMe - this is not elegant and depends on lots of assumws knowledge about the metrics
    # Bronze requires:  Having a License and Readme.
    # FixMe - may be >1 score if user has gone back and forth in the UI
    # prolly best to stop that happening in the first place

    # License
    # FixMe - implement get_score
    license_scores = Score.query.filter_by(software_id=software_id, short_description="Has a license file?")
    license_score = license_scores.first().value
    app.logger.info("License Score: " + str(license_score))
    if license_score < 50:
        return False

    # ReadMe
    readme_scores = Score.query.filter_by(software_id=software_id, short_description="Has a README file?")
    readme_score = readme_scores.first().value
    app.logger.info("README Score: " + str(readme_score))
    if readme_score != 100:
        return False

    return True


def has_silver_award(software_id):
    """
    Ascertain if the piece of software had passed metrics to achieve a silver award
    :param software_id:
    :return: True if passed, otherwise false
    """
    # FixMe - this is not elegant and depends on lots of assumed knowledge about the metrics
    # Silver requires:  Having a License and Readme.
    # FixMe - may be >1 score if user has gone back and forth in the UI
    # prolly best to stop that happening in the first place

    # Vitality
    vitality_scores = Score.query.filter_by(software_id=software_id, short_description="Calculate committer trend")
    vitality_score = vitality_scores.first().value
    app.logger.info("Vitality Score: " + str(vitality_score))
    if vitality_score < 50:
        return False

    return True


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
            if metric.IDENTIFIER == metric_id:
                app.logger.info("Running metric: " + metric.SHORT_DESCRIPTION)
                metric.run(software=sw, form_data=value)
                app.logger.info(metric.get_score())
                app.logger.info(metric.get_feedback())
                score = Score(software_id=sw.id,
                              name=metric.NAME,
                              identifier=metric.IDENTIFIER,
                              category=metric.CATEGORY,
                              short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION,
                              interactive=metric.SELF_ASSESSMENT,
                              value=metric.get_score(),
                              feedback=metric.get_feedback(),
                              category_importance=form_data['importance'],
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
            if metric.IDENTIFIER == metric_id:
                app.logger.info("Running metric: " + metric.SHORT_DESCRIPTION)
                metric.run(software=sw, helper=repos_helper)
                app.logger.info(metric.get_score())
                app.logger.info(metric.get_feedback())
                score = Score(software_id=sw.id,
                              name=metric.NAME,
                              identifier=metric.IDENTIFIER,
                              category=metric.CATEGORY,
                              short_description=metric.SHORT_DESCRIPTION,
                              long_description=metric.LONG_DESCRIPTION,
                              interactive=metric.SELF_ASSESSMENT,
                              value=metric.get_score(),
                              feedback=metric.get_feedback(),
                              category_importance=form_data['importance'],
                              metric_importance=form_data['IMPORTANCE_' + metric_id])
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