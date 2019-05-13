from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NewListForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  submit = SubmitField('Save')

class ConfirmDeleteForm(FlaskForm):
  yes = SubmitField('Confirm')
  no = SubmitField('I regret my decision')
