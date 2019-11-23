from flask import jsonify, request
from flask_login import current_user
from app.models import List
from app.api import bp
from app.api.decorators import list_access_required, login_required
from app.api.helpers import extract_args


@bp.route("/days", methods=["GET"])
@login_required
def get_days():
    args = extract_args(request.args)
    lists = current_user.get_lists()
    days = [
        l.get_or_create_days(
            args["offset"], args["limit"], args["start_today"]
        )
        for l in lists
    ]
    json_obj_days = [day.to_dict() for sublist in days for day in sublist]
    return jsonify(json_obj_days), 200


@bp.route("/lists/<list_id>/days", methods=["GET"])
@login_required
@list_access_required
def get_days_by_list(list_id):
    args = extract_args(request.args)
    list_ = List.query.filter_by(id=list_id).first()
    days = list_.get_or_create_days(
        args["offset"], args["limit"], args["start_today"]
    )
    json_obj = [
        {
            "day": d.day,
            "id": d.id,
            "entries": [e.id for e in d.get_or_create_entries()],
        }
        for d in days
    ]
    return jsonify(json_obj), 200
