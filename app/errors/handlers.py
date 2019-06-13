from app import db
from flask import render_template, jsonify
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
  db.session.rollback()
  return jsonify({'msg': 'Something went wrong!' + error}), 500
