from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


def check_confirmed(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if current_user.is_confirmed is False:
      return redirect(url_for('unconfirmed'))
    return func(*args, **kwargs)
  return decorated_function