from flask import jsonify, request
from flask_login import login_user, current_user, logout_user
from app.models import User
from app import db
from app.api import bp
from app.api.decorators import login_required
from app.api.exceptions import APIError


@bp.route("/users", methods=["GET"])
@login_required
def get_users():
    users = User.query.all()
    users = [i.to_dict() for i in users]
    return jsonify(users), 200


def verify_mandatory_user_fields(req):
    if "username" not in req:
        raise APIError("username is required")
    if "email" not in req:
        raise APIError("email is required")
    if "firstname" not in req:
        raise APIError("firstname is required")
    if "lastname" not in req:
        raise APIError("lastname is required")


@bp.route("/users", methods=["POST"])
def register():
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    verify_mandatory_user_fields(req)
    if "password" not in req:
        raise APIError("password is required")
    if User.query.filter_by(username=req["username"]).first():
        raise APIError("Username already taken")
    if User.query.filter_by(email=req["email"]).first():
        raise APIError("Email already taken")
    if len(req["password"]) < 8:
        raise APIError(
            "Password is too short, please use 8 characters or more"
        )
    u = User(
        username=req["username"],
        email=req["email"],
        firstname=req["firstname"],
        lastname=req["lastname"],
        is_confirmed=False,
    )
    u.set_password(req["password"])
    db.session.add(u)
    db.session.commit()
    # TODO confirm email
    # token = generate_confirmation_token(u.email)
    # confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    # send_user_confirmation_email(u, confirm_url)
    login_user(u)
    return jsonify({"msg": "Registered successfully", **u.to_dict()}), 201


@bp.route("/users/<user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    user_ = User.query.filter_by(id=user_id).first()
    if not user_:
        raise APIError(f"No user with id {user_id}", 404)
    if user_ != current_user:
        raise APIError("You cannot delete another user", 403)
    db.session.delete(user_)
    db.session.commit()
    logout_user()
    return jsonify({"msg": "User deleted"}), 401


@bp.route("/users/<user_id>", methods=["PUT"])
@login_required
def put_users(user_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    user_ = User.query.filter_by(id=user_id).first()
    if not user_:
        raise APIError(f"User with id {user_id} not found", 404)
    if not user_ == current_user:
        raise APIError("Insufficient permissions", 403)
    verify_mandatory_user_fields(req)
    if "password" in req and req["password"] != "":
        if len(req["password"]) < 8:
            raise APIError(
                "Password is too short, please use 8 characters or more"
            )
        else:
            current_user.set_password(req["password"])
    if req["username"] != current_user.username:
        if User.query.filter_by(username=req["username"]).first():
            raise APIError("Username already taken")
        current_user.username = req["username"]
    if req["email"] != current_user.email:
        if User.query.filter_by(email=req["email"]).first():
            raise APIError("Email already taken")
        current_user.email = req["email"]
    # TODO confirm email
    # token = generate_confirmation_token(u.email)
    # confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    # send_user_confirmation_email(u, confirm_url)
    current_user.firstname = req["firstname"]
    current_user.lastname = req["lastname"]
    db.session.commit()
    return (
        jsonify(
            {"msg": "User updated successfully", **current_user.to_dict()}
        ),
        200,
    )
