from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError
from app.models import User

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


class ShareForm(FlaskForm):
  target = StringField('Who do you want to share with?',
                       validators=[DataRequired()])
  submit = SubmitField('Share')

  def validate_target(self, target):
    user = User.query.filter_by(username=target.data.lower()).first()
    if user is None:
      user = User.query.filter_by(email=target.data.lower()).first()
      if user is None:
        raise ValidationError('User does not exist.')
    if user == current_user:
      raise ValidationError('You can not share a list with yourself.')
