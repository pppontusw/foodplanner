from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user
from app.models import List, Entry, User
from app.api.exceptions import APIError


def check_confirmed(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if current_user.is_confirmed is False:
      return jsonify({'msg': 'You need to confirm your email'}), 403
    return func(*args, **kwargs)
  return decorated_function


def list_access_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    list_id = kwargs['list_id']
    list_ = List.query.filter_by(id=list_id).first()
    if current_user not in list_.get_users_with_access():
      raise APIError('You don\'t have access to this page', 403)
    return func(*args, **kwargs)
  return decorated_function


def list_owner_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    list_id = kwargs['list_id']
    list_ = List.query.filter_by(id=list_id).first()
    if current_user not in list_.get_owners():
      raise APIError('Only the list owner can perform this action', 403)
    return func(*args, **kwargs)
  return decorated_function


def entry_access_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    entry_id = kwargs['entry_id']
    entry = Entry.query.filter_by(id=entry_id).first()
    list_ = entry.day.list_
    if current_user not in list_.get_users_with_access():
      raise APIError('You don\'t have access to this page', 403)
    return func(*args, **kwargs)
  return decorated_function


def login_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if not current_user.is_authenticated:
      raise APIError('Please log in', 401)
    return func(*args, **kwargs)
  return decorated_function
