from flask import jsonify, request
from flask_login import login_user, current_user, logout_user
from app.models import User
from app.api import bp
from app.api.decorators import login_required
from app.api.exceptions import APIError


@bp.route("/auth/login", methods=["POST"])
def login():
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "username" not in req:
        raise APIError("username is required")
    if "password" not in req:
        raise APIError("password is required")
    u = User.query.filter_by(username=req["username"]).first()
    if u is None or not u.check_password(req["password"]):
        raise APIError("Invalid username or password!", 401)
    login_user(u)
    return jsonify({"msg": "Logged in successfully", **u.to_dict()}), 200


@bp.route("/auth/user", methods=["GET"])
def user():
    if current_user.is_authenticated:
        return (
            jsonify({"msg": "Session still valid", **current_user.to_dict()}),
            200,
        )
    raise APIError("Please log in", 401)


@bp.route("/auth/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Logged out successfully"}), 200
