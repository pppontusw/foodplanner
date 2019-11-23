from flask import jsonify, request
from app.models import List, Food, FoodCategory, FoodCategoryAssociation
from app import db
from app.api import bp
from app.api.decorators import list_access_required, login_required
from app.api.exceptions import APIError


@bp.route("/lists/<list_id>/foods", methods=["GET"])
@login_required
@list_access_required
def get_foods(list_id):
    list_ = List.query.filter_by(id=list_id).first()
    json_obj = [food.to_dict() for food in list_.foods]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/foods/<food_id>", methods=["PUT"])
@login_required
@list_access_required
def put_food(list_id, food_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "name" not in req:
        raise APIError("name is required")
    if "categories" not in req:
        raise APIError("categories is required")
    list_ = List.query.filter_by(id=list_id).first()
    food = Food.query.filter_by(list_id=list_.id, id=food_id).first()
    if not food:
        raise APIError(f"No food with id {food_id} exists", 404)
    food.name = req["name"]
    categories_to_associate = [
        i for i in list_.categories if i.name in req["categories"]
    ]
    categories_to_disassociate = [
        i for i in list_.categories if i.name not in req["categories"]
    ]
    categories_to_add = [
        i
        for i in req["categories"]
        if i not in [i.name for i in categories_to_associate]
    ]
    for category in categories_to_add:
        fc = FoodCategory(list_id=list_.id, name=category)
        db.session.add(fc)
        db.session.commit()
        fca = FoodCategoryAssociation(category_id=fc.id, food_id=food.id)
        db.session.add(fca)
        db.session.commit()
    for category in categories_to_associate:
        if category.id not in [i.category.id for i in food.categories]:
            fca = FoodCategoryAssociation(
                category_id=category.id, food_id=food.id
            )
            db.session.add(fca)
    for category in categories_to_disassociate:
        if category in [i.category for i in food.categories]:
            fca = FoodCategoryAssociation.query.filter_by(
                category_id=category.id, food_id=food.id
            ).first()
            db.session.delete(fca)
    db.session.commit()
    json_obj = [food.to_dict() for food in list_.foods]
    return jsonify(json_obj)


@bp.route("/lists/<list_id>/foods/<food_id>", methods=["DELETE"])
@login_required
@list_access_required
def delete_food(list_id, food_id):
    list_ = List.query.filter_by(id=list_id).first()
    food = Food.query.filter_by(list_id=list_.id, id=food_id).first()
    if not food:
        raise APIError(f"No meal with id {food_id} exists", 404)
    db.session.delete(food)
    db.session.commit()
    json_obj = [food.to_dict() for food in list_.foods]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/foods", methods=["POST"])
@login_required
@list_access_required
def post_foods(list_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "name" not in req:
        raise APIError("name is required")
    list_ = List.query.filter_by(id=list_id).first()
    if Food.query.filter_by(name=req["name"], list_id=list_.id).first():
        raise APIError(f'Food {req["name"]} already exists')
    food = Food(list_id=list_.id, name=req["name"])
    db.session.add(food)
    db.session.commit()
    json_obj = [food.to_dict() for food in list_.foods]
    return jsonify(json_obj), 201
