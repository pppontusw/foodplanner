from app import db
from flask import render_template, jsonify
from app.errors import bp
from app.api.exceptions import APIError


@bp.app_errorhandler(APIError)
def handle_api_error(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


@bp.app_errorhandler(404)
def not_found_error(error):
  response = jsonify({'msg': 'Not Found'})
  response.status_code = 404
  return response
  # return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
  db.session.rollback()
  response = jsonify({'msg': 'Internal Server Error'})
  response.status_code = 500
  return response
