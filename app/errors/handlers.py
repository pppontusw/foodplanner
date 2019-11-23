from flask import jsonify, current_app
from app import db
from app.errors import bp
from app.api.exceptions import APIError


@bp.app_errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@bp.app_errorhandler(404)
def not_found_error(error):
    response = jsonify({"msg": "Not Found"})
    current_app.logger.error(error)
    response.status_code = 404
    return response


@bp.app_errorhandler(405)
def method_not_allowed(error):
    response = jsonify({"msg": "Method Not Allowed"})
    current_app.logger.error(error)
    response.status_code = 405
    return response


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    current_app.logger.error(error)
    response = jsonify({"msg": "Internal Server Error"})
    response.status_code = 500
    return response
