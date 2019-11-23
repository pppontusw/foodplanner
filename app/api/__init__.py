# flake8: noqa
from flask import Blueprint

bp = Blueprint("api", __name__)
from app.api import (
    routes,
    decorators,
    lists,
    settings,
    auth,
    users,
    meals,
    shares,
    categories,
    entries,
    days,
    foods,
)
