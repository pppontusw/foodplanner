from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user
from app.models import User


class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  firstname = StringField('First name', validators=[DataRequired()])
  lastname = StringField('Last name', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
      'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data.lower()).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data.lower()).first()
    if user is not None:
      raise ValidationError('Please use a different username.')


class ProfileForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  firstname = StringField('First name', validators=[DataRequired()])
  lastname = StringField('Last name', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[])
  password2 = PasswordField(
      'Repeat Password', validators=[EqualTo('password')])
  submit = SubmitField('Save')

  def validate_email(self, email):
    if email.data.lower() != current_user.email:
      user = User.query.filter_by(email=email.data.lower()).first()
      if user is not None and user != current_user:
        raise ValidationError('Please use a different email address.')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data.lower()).first()
    if user is not None and user != current_user:
      raise ValidationError('Please use a different username.')


class ResetPasswordRequestForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Request Password Reset')


class ConfirmDeleteForm(FlaskForm):
  yes = SubmitField('Confirm')
  no = SubmitField('I regret my decision')


class ResetPasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
      'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Request Password Reset')
