from flask import current_app
from app.api.exceptions import APIError
from app.api import bp


# This is here for the testing
# of the flask 500 error handler
@bp.route("/zerodivision")
def zerodiv():
    if current_app.config["TESTING_500"]:
        return 1 / 0
    raise APIError("Not found", 404)
