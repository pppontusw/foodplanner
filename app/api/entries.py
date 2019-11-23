from flask import jsonify, request
from flask_login import current_user
from app.models import List, Entry
from app import db
from app.api import bp
from app.api.decorators import (
    list_access_required,
    login_required,
    entry_access_required,
)
from app.api.exceptions import APIError
from app.api.helpers import extract_args


@bp.route("/entries", methods=["GET"])
@login_required
def get_entries():
    args = extract_args(request.args)
    lists = current_user.get_lists()
    days = [
        l.get_or_create_days(
            args["offset"], args["limit"], args["start_today"]
        )
        for l in lists
    ]
    entries = [d.get_or_create_entries() for sublist in days for d in sublist]
    json_obj_entries = [e.to_dict() for sublist in entries for e in sublist]
    return jsonify(json_obj_entries), 200


@bp.route("/entries/<entry_id>", methods=["PATCH"])
@login_required
@entry_access_required
def patch_entry(entry_id):
    # TODO functionize -> get_json -> check that there is content (or raise)
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    entry.value = req["value"]
    db.session.commit()
    return jsonify(entry.to_dict()), 200


@bp.route("/lists/<list_id>/entries", methods=["GET"])
@login_required
@list_access_required
def get_entries_by_list(list_id):
    args = extract_args(request.args)
    list_ = List.query.filter_by(id=list_id).first()
    days = list_.get_or_create_days(
        args["offset"], args["limit"], args["start_today"]
    )
    entries = [e.get_or_create_entries() for e in days]
    json_obj = [e.to_dict() for sublist in entries for e in sublist]
    return jsonify(json_obj), 200
