import calendar
from flask import jsonify, request
from flask_login import current_user
from app.models import List
from app import db
from app.api import bp
from app.api.decorators import list_access_required, login_required
from app.api.exceptions import APIError
from app.api.helpers import extract_args


@bp.route("/lists/<list_id>/settings", methods=["PUT"])
@login_required
@list_access_required
def put_list_settings(list_id):
    args = extract_args(request.args)

    req = request.get_json()
    if not req:
        raise APIError("application/json is required")

    list_ = List.query.filter_by(id=list_id).first()
    settings = list_.get_settings_for_user(current_user)

    if "start_day_of_week" not in req:
        raise APIError("start_day_of_week is required")
    if "days_to_display" not in req:
        raise APIError("days_to_display is required")

    # handle days_to_display
    days_to_display = int(req["days_to_display"])
    if days_to_display < 5 or days_to_display > 21:
        raise APIError("days_to_display needs to be a number between 5-21")

    # handle start_day_of_week
    allowed_days = list(calendar.day_name)
    allowed_days.append("Today")
    start_day_of_week = req["start_day_of_week"]
    if start_day_of_week not in allowed_days:
        raise APIError(
            f'start_day_of_week needs to be one of:  {" ".join(allowed_days)}'
        )
    if start_day_of_week == "Today":
        start_day_of_week = -1
    else:
        start_day_of_week = allowed_days.index(start_day_of_week)

    # set and commit
    settings.start_day_of_week = start_day_of_week
    settings.days_to_display = days_to_display
    db.session.commit()

    return jsonify(
        [list_.to_dict(args["offset"], args["limit"], args["start_today"])]
    )
