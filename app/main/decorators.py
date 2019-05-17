from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models import List, Entry

def check_confirmed(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if current_user.is_confirmed is False:
      return redirect(url_for('auth.unconfirmed'))
    return func(*args, **kwargs)
  return decorated_function


def check_list_access(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    list_id = kwargs['list_id']
    list_ = List.query.filter_by(id=list_id).first()
    if current_user.id not in list_.get_users_with_access():
      flash('You don\'t have access to this page', 'danger')
      return redirect(url_for('auth.login'))
    return func(*args, **kwargs)
  return decorated_function


def check_list_owner(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    list_id = kwargs['list_id']
    list_ = List.query.filter_by(id=list_id).first()
    if current_user.id != list_.owner.id:
      flash('Only the list owner can delete the list!', 'danger')
      return redirect(url_for('auth.login'))
    return func(*args, **kwargs)
  return decorated_function

def check_entry_access(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    entry_id = kwargs['entry_id']
    entry = Entry.query.filter_by(id=entry_id).first()
    list_ = entry.day.list_
    if current_user.id not in list_.get_users_with_access():
      flash('You don\'t have access to this page', 'danger')
      return redirect(url_for('auth.login'))
    return func(*args, **kwargs)
  return decorated_function
