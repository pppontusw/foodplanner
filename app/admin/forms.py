from flask_wtf import FlaskForm
from wtforms import SubmitField

class ConfirmDeleteForm(FlaskForm):
  yes = SubmitField('Confirm')
  no = SubmitField('I regret my decision')
