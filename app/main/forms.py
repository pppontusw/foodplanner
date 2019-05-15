from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class NewListForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  submit = SubmitField('Save')

class ConfirmDeleteForm(FlaskForm):
  yes = SubmitField('Confirm')
  no = SubmitField('I regret my decision')


class ListSettingsForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  startDayOfTheWeek = SelectField('Starting Day of the Week', choices=[
      (-1, 'Today'), (0, 'Monday'), (1, 'Tuesday'),
      (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'),
      (5, 'Saturday'), (6, 'Sunday')
      ], coerce=int)
  daysToDisplay = SelectField('Days per page', choices=[(i, i) for i in range(5, 21)], coerce=int)
  submit = SubmitField('Save')
