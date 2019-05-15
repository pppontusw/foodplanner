from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app.models import User
from app.admin.decorators import admin_required
from app.admin.forms import ConfirmDeleteForm
from app.admin import bp
from app import db

@bp.route('/index')
@login_required
@admin_required
def index():
  userquery = User.query.all()
  return render_template('admin/index.html', users=userquery)

@bp.route('/confirmuser/<uid>')
@login_required
@admin_required
def confirmuser(uid):
  user = User.query.filter(User.id == uid).first_or_404()
  user.is_confirmed = True
  db.session.commit()
  flash('Email confirmed successfully!', 'success')
  return redirect(url_for('admin.index'))


@bp.route('/unconfirmuser/<id>')
@login_required
@admin_required
def unconfirmuser(uid):
  user = User.query.filter(User.id == uid).first_or_404()
  user.is_confirmed = False
  db.session.commit()
  flash('Email unconfirmed successfully!', 'success')
  return redirect(url_for('admin.index'))


@bp.route('/deluser/<uid>', methods=['GET', 'POST'])
@login_required
@admin_required
def deluser(uid):
  form = ConfirmDeleteForm()
  if form.validate_on_submit():
    if 'yes' in request.form:
      user = User.query.filter(User.id == uid).first_or_404()
      user.delete_user()
      flash('Account deleted successfully!', 'success')
      return redirect(url_for('admin.index'))
    else:
      return redirect(url_for('admin.index'))
  user = User.query.filter(User.id == uid).first_or_404()
  return render_template('admin/confirm_delete_admin.html', user=user, form=form)
