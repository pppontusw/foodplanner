from flask import jsonify, request
from app.models import List, Meal
from app import db
from app.api import bp
from app.api.decorators import list_access_required, login_required
from app.api.exceptions import APIError


@bp.route("/lists/<list_id>/meals", methods=["GET"])
@login_required
@list_access_required
def get_meals(list_id):
    list_ = List.query.filter_by(id=list_id).first()
    json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/meals/<meal_id>", methods=["DELETE"])
@login_required
@list_access_required
def delete_meal(list_id, meal_id):
    list_ = List.query.filter_by(id=list_id).first()
    meal = Meal.query.filter_by(list_id=list_.id, id=meal_id).first()
    if not meal:
        raise APIError(f"No meal with id {meal_id} exists", 404)
    db.session.delete(meal)
    db.session.commit()
    json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/meals/<meal_id>", methods=["PATCH"])
@login_required
@list_access_required
def patch_meals(list_id, meal_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "name" not in req:
        raise APIError("name is required")
    list_ = List.query.filter_by(id=list_id).first()
    meal = Meal.query.filter_by(list_id=list_.id, id=meal_id).first()
    if not meal:
        raise APIError(f"No meal with id {meal_id} exists", 404)
    meal.name = req["name"]
    db.session.commit()
    json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/meals", methods=["POST"])
@login_required
@list_access_required
def post_meals(list_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "name" not in req:
        raise APIError("name is required")
    list_ = List.query.filter_by(id=list_id).first()
    if Meal.query.filter_by(name=req["name"], list_id=list_.id).first():
        raise APIError(f'Meal {req["name"]} already exists')
    try:
        order = 1 + max(
            [i.order for i in Meal.query.filter_by(list_id=list_.id).all()]
        )
    except ValueError:
        order = 1
    meal = Meal(list_id=list_.id, name=req["name"], order=order)
    db.session.add(meal)
    db.session.commit()
    json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
    return jsonify(json_obj), 201


def verify_meals(req, meals):
    for meal in req:
        if "id" in meal:
            if meal["id"] not in [i.id for i in meals]:
                raise APIError(
                    "ID assignment not allowed, only include pre-existing IDs"
                )
            if "name" not in meal:
                raise APIError(f"No name received in {meal}")


@bp.route("/lists/<list_id>/meals", methods=["PUT"])
@login_required
@list_access_required
def put_meals(list_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if not isinstance(req, list):
        raise APIError("A list of meals is required")
    list_ = List.query.filter_by(id=list_id).first()
    meals = Meal.query.filter_by(list_id=list_.id).all()
    # verify integrity of received list
    verify_meals(req, meals)
    for meal in meals:
        if meal.id not in [i["id"] for i in req if "id" in i]:
            db.session.delete(meal)
    db.session.commit()
    meals = Meal.query.filter_by(list_id=list_.id).all()
    for index, req_meal in enumerate(req):
        if "id" in req_meal and req_meal["id"] in [i.id for i in meals]:
            meals_index = [i.id for i in meals].index(req_meal["id"])
            meals[meals_index].order = index
            meals[meals_index].name = req_meal["name"]
        else:
            new_meal = Meal(
                list_id=list_.id, name=req_meal["name"], order=index
            )
            db.session.add(new_meal)
    db.session.commit()
    json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
    return jsonify(json_obj)
