from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


def admin_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if current_user.is_admin is not True:
      return redirect(url_for('main.index'))
    return func(*args, **kwargs)
  return decorated_function
