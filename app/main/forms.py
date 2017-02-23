from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired

# Forms for webapp.  Uses WTForms

class SoftwareSubmitForm(FlaskForm):
    """
    Form for initial submission of software for evaluation
    """
    name = StringField('Software Name', validators=[DataRequired()])
    description = TextAreaField('Description', render_kw={"rows": 10})
    version = StringField('Version')
    url = StringField('Repository URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()