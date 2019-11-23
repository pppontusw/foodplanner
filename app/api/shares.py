from flask import jsonify, request
from app.models import List, ListPermission, User
from app import db
from app.api import bp
from app.api.decorators import (
    list_access_required,
    login_required,
    list_owner_required,
)
from app.api.exceptions import APIError


@bp.route("/lists/<list_id>/shares", methods=["GET"])
@login_required
@list_access_required
def get_list_shares(list_id):
    list_ = List.query.filter_by(id=list_id).first()
    return jsonify([i.to_dict() for i in list_.users]), 200


@bp.route("/lists/<list_id>/shares", methods=["POST"])
@login_required
@list_access_required
@list_owner_required
def post_list_shares(list_id):
    list_ = List.query.filter_by(id=list_id).first()
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "username" not in req:
        raise APIError("Username is required")
    user_ = User.query.filter_by(username=req["username"]).first()
    if not user_:
        raise APIError(f"User {req['username']} does not exist", 404)
    if user_ in list_.get_users_with_access():
        raise APIError(
            f"User {req['username']} already has access to this list"
        )
    new_perm = ListPermission(
        user_id=user_.id, list_id=list_.id, permission_level="member"
    )
    db.session.add(new_perm)
    db.session.commit()
    return jsonify([i.to_dict() for i in list_.users]), 201


@bp.route("/lists/<list_id>/shares/<share_id>", methods=["DELETE"])
@login_required
@list_access_required
@list_owner_required
def delete_share(list_id, share_id):
    list_ = List.query.filter_by(id=list_id).first()
    share = ListPermission.query.filter_by(
        id=share_id, list_id=list_id
    ).first()
    if not share:
        raise APIError(f"Share with id {share_id} not found", 404)
    db.session.delete(share)
    db.session.commit()
    return jsonify([i.to_dict() for i in list_.users]), 200
