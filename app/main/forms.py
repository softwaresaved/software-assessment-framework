from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

# Forms for webapp.  Uses WTForms

class SoftwareSubmitForm(FlaskForm):
    """
    Form for initial submission of software for evaluation
    """
    name = StringField('Software Name', validators=[DataRequired()])
    description = TextAreaField('Description', render_kw={"rows": 10})
    version = StringField('Version')
    url = StringField('Repository URL')
    submit = SubmitField('Submit')