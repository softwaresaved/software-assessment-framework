from datetime import datetime
from flask import render_template, redirect, url_for
from app.main.forms import SoftwareSubmitForm
from app.models import db, Software
from app import app

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
                      submitted=datetime.utcnow(),
                      url=softwareSubmitForm.url.data)

        # Persist it
        db.session.add(sw)
        db.session.commit()
        # Forward to metrics selection
        return redirect(url_for('metrics_selection'))

    return render_template('index.html', form=softwareSubmitForm)


@app.route('/metrics_selection')
def metrics_selection():
    # ToDo Load metrics and add descriptions

    return(render_template('metrics_selection.html'))