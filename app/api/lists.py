from flask import jsonify, request
from flask_login import current_user
from app.models import List, ListPermission
from app import db
from app.api import bp
from app.api.decorators import (
    list_access_required,
    login_required,
    list_owner_required,
)
from app.api.exceptions import APIError
from app.api.helpers import extract_args


@bp.route("/lists", methods=["GET"])
@login_required
def get_lists():
    args = extract_args(request.args)
    lists = current_user.get_lists()
    json_obj = [
        l.to_dict(args["offset"], args["limit"], args["start_today"])
        for l in lists
    ]
    return jsonify(json_obj), 200


@bp.route("/lists", methods=["POST"])
@login_required
def post_list():
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "listname" not in req:
        raise APIError("listname is required")
    if req["listname"] == "":
        raise APIError("Listname cannot be empty")
    list_ = List(name=req["listname"])
    list_.generate_api_key()
    db.session.add(list_)
    db.session.commit()
    perm = ListPermission(
        list_id=list_.id, user_id=current_user.id, permission_level="owner"
    )
    db.session.add(perm)
    db.session.commit()
    return jsonify(list_.to_dict()), 201


@bp.route("/lists/<list_id>", methods=["GET"])
@login_required
@list_access_required
def get_list(list_id):
    args = extract_args(request.args)
    list_ = List.query.filter_by(id=list_id).first()
    return (
        jsonify(
            [list_.to_dict(args["offset"], args["limit"], args["start_today"])]
        ),
        200,
    )


@bp.route("/lists/<list_id>", methods=["PATCH"])
@login_required
@list_access_required
def patch_list(list_id):
    args = extract_args(request.args)
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    list_ = List.query.filter_by(id=list_id).first()
    if "listname" in req:
        list_.name = req["listname"]
    db.session.commit()
    return (
        jsonify(
            [list_.to_dict(args["offset"], args["limit"], args["start_today"])]
        ),
        200,
    )


@bp.route("/lists/<list_id>", methods=["DELETE"])
@login_required
@list_owner_required
@list_access_required
def delete_list(list_id):
    args = extract_args(request.args)
    list_ = List.query.filter_by(id=list_id).first()
    db.session.delete(list_)
    db.session.commit()
    lists = current_user.get_lists()
    json_obj = [
        l.to_dict(args["offset"], args["limit"], args["start_today"])
        for l in lists
    ]
    return jsonify(json_obj), 200
