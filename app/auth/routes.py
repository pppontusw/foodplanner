from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
from app.auth.token import generate_confirmation_token, confirm_token
from app.auth import bp
from app.auth.email import send_password_reset_email, send_user_confirmation_email
from app.auth.forms import LoginForm, RegistrationForm, ProfileForm
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm, ConfirmDeleteForm
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = LoginForm()
  if form.validate_on_submit():
    u = User.query.filter_by(username=form.username.data.lower()).first()
    if u is None or not u.check_password(form.password.data):
      flash('Invalid username or password', 'danger')
      return redirect(url_for('auth.login'))
    login_user(u, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('main.index')
    return redirect(next_page)
  return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():
  form = ProfileForm()
  if request.method == 'GET':
    form.email.data = current_user.email
    form.username.data = current_user.username
    form.firstname.data = current_user.firstname
    form.lastname.data = current_user.lastname
  if form.validate_on_submit():
    if current_user.email != form.email.data.lower():
      current_user.email = form.email.data.lower()
      current_user.is_confirmed = False
      db.session.commit()
      token = generate_confirmation_token(current_user.email)
      confirm_url = url_for('auth.confirm_email', token=token, _external=True)
      send_user_confirmation_email(current_user, confirm_url)
      flash('Email changed! A confirmation email has been sent to verify your new email. '
            + 'Please note that you will not receive status emails until you verify the new email.',
            'info')
    if current_user.username != form.username.data.lower():
      current_user.username = form.username.data.lower()
      db.session.commit()
      flash('Username changed!', 'info')
    if current_user.firstname != form.firstname.data:
      current_user.firstname = form.firstname.data
      db.session.commit()
      flash('First name changed!', 'info')
    if current_user.lastname != form.lastname.data:
      current_user.lastname = form.lastname.data
      db.session.commit()
      flash('Last name changed!', 'info')
    if form.password.data == "":
      return redirect(url_for('main.index'))
    elif len(form.password.data) >= 8 and not current_user.check_password(form.password.data):
      current_user.set_password(form.password.data)
      db.session.commit()
      flash("Password changed successfully!", 'success')
      return redirect(url_for('main.index'))
    elif len(form.password.data) < 8:
      flash("Password needs to be 8 characters or more.", 'danger')
  return render_template('auth/user.html', user=current_user, form=form)


@bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    if len(form.password.data) >= 8:
      u = User(
          username=form.username.data.lower(),
          email=form.email.data.lower(),
          firstname=form.firstname.data,
          lastname=form.lastname.data,
          is_confirmed=False
      )
      u.set_password(form.password.data)
      db.session.add(u)
      db.session.commit()
      flash('Account successfully registered', 'success')
      token = generate_confirmation_token(u.email)
      confirm_url = url_for('auth.confirm_email', token=token, _external=True)
      send_user_confirmation_email(u, confirm_url)
      login_user(u)
      flash('A confirmation email has been sent via email.', 'info')
      return redirect(url_for('auth.login'))
    else:
      flash('Password needs to be 8 characters or more!', 'danger')
  return render_template('auth/register.html', title='Register', form=form)


@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
  email = confirm_token(token)
  if not email:
    flash('The confirmation link is invalid or has expired.', 'danger')
  u = User.query.filter_by(email=email).first_or_404()
  if u.is_confirmed:
    flash('Account already confirmed. Please login.', 'warning')
  else:
    u.is_confirmed = True
    db.session.commit()
    flash('You have confirmed your account. Thanks!', 'success')
  return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = ResetPasswordRequestForm()
  if form.validate_on_submit():
    u = User.query.filter_by(email=form.email.data.lower()).first()
    if u:
      send_password_reset_email(u)
    flash('Check your email for the instructions to reset your password', 'info')
    return redirect(url_for('auth.login'))
  return render_template('auth/reset_password_request.html',
                         title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  u = User.verify_reset_password_token(token)
  if not u:
    return redirect(url_for('main.index'))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    u.set_password(form.password.data)
    db.session.commit()
    flash('Your password has been reset.', 'info')
    return redirect(url_for('auth.login'))
  return render_template('auth/reset_password.html', form=form)


@bp.route('/unconfirmed')
@login_required
def unconfirmed():
  if current_user.is_confirmed:
    return redirect(url_for('main.index'))
  flash('Please confirm your email!', 'info')
  return render_template('auth/unconfirmed.html')


@bp.route('/confirm_delete')
@login_required
def confirm_delete():
  return render_template('auth/confirm_delete.html')


@bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
  form = ConfirmDeleteForm()
  if form.validate_on_submit():
    if 'yes' in request.form:
      current_user.delete_user()
      logout_user()
      flash('Account deleted successfully!', 'success')
      return redirect(url_for('main.index'))
    else:
      return redirect(url_for('main.index'))
  return render_template('auth/confirm_delete.html', form=form)


@bp.route('/resend')
@login_required
def resend_confirmation():
  token = generate_confirmation_token(current_user.email)
  confirm_url = url_for('auth.confirm_email', token=token, _external=True)
  send_user_confirmation_email(current_user, confirm_url)
  flash('A confirmation email has been sent via email.', 'info')
  return redirect(url_for('auth.unconfirmed'))
