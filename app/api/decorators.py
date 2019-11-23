from functools import wraps
from flask_login import current_user
from app.models import List, Entry
from app.api.exceptions import APIError

# TODO is this needed?
# def check_confirmed(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if current_user.is_confirmed is False:
#             raise APIError('You need to confirm your email', 403)
#         return func(*args, **kwargs)
#     return decorated_function


def list_access_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        list_id = kwargs["list_id"]
        list_ = List.query.filter_by(id=list_id).first()
        if not list_:
            raise APIError(f"No list with id {list_id}", 404)
        if current_user not in list_.get_users_with_access():
            raise APIError("You don't have access to this page", 403)
        return func(*args, **kwargs)

    return decorated_function


def list_owner_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        list_id = kwargs["list_id"]
        list_ = List.query.filter_by(id=list_id).first()
        if not list_:
            raise APIError(f"No list with id {list_id}", 404)
        if current_user not in list_.get_owners():
            raise APIError("Only the list owner can perform this action", 403)
        return func(*args, **kwargs)

    return decorated_function


def entry_access_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        entry_id = kwargs["entry_id"]
        entry = Entry.query.filter_by(id=entry_id).first()
        if not entry:
            raise APIError(f"No entry with id {entry_id}", 404)
        list_ = entry.day.list_
        if current_user not in list_.get_users_with_access():
            raise APIError("You don't have access to this page", 403)
        return func(*args, **kwargs)

    return decorated_function


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise APIError("Please log in", 401)
        return func(*args, **kwargs)

    return decorated_function
