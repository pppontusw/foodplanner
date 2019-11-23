from flask import jsonify, request
from app.models import List, Food, FoodCategory, FoodCategoryAssociation
from app import db
from app.api import bp
from app.api.decorators import list_access_required, login_required
from app.api.exceptions import APIError


@bp.route("/lists/<list_id>/categories", methods=["GET"])
@login_required
@list_access_required
def get_categories_by_list(list_id):
    list_ = List.query.filter_by(id=list_id).first()
    json_obj = [i.to_dict() for i in list_.categories]
    return jsonify(json_obj), 200


@bp.route("/lists/<list_id>/categories", methods=["POST"])
@login_required
@list_access_required
def post_categories(list_id):
    req = request.get_json()
    if not req:
        raise APIError("application/json is required")
    if "name" not in req:
        raise APIError("name is required")
    list_ = List.query.filter_by(id=list_id).first()
    if req["name"] in [i.name for i in list_.categories]:
        raise APIError(f'FoodCategory {req["name"]} already exists')
    foodcategory = FoodCategory(name=req["name"], list_id=list_id)
    db.session.add(foodcategory)
    db.session.commit()
    json_obj = [category.to_dict() for category in list_.categories]
    return jsonify(json_obj), 201


@bp.route("/lists/<list_id>/categories/<category_id>", methods=["DELETE"])
@login_required
@list_access_required
def delete_category_by_list(list_id, category_id):
    list_ = List.query.filter_by(id=list_id).first()
    category = FoodCategory.query.filter_by(id=category_id).first()
    if not category:
        raise APIError(f"No category with id {category_id} exists", 404)
    db.session.delete(category)
    db.session.commit()
    json_obj = [category.to_dict() for category in list_.categories]
    return jsonify(json_obj), 200


@bp.route("/foods/<food_id>/categories", methods=["GET"])
@login_required
# TODO access control
# @list_access_required
def get_categories_by_food(food_id):
    food = Food.query.filter_by(id=food_id).first()
    if not food:
        raise APIError(f"No food with id {food_id} exists", 404)
    json_obj = [category.category.to_dict() for category in food.categories]
    return jsonify(json_obj)


@bp.route("/foods/<food_id>/categories/<category_id>", methods=["POST"])
@login_required
# TODO access control
# @list_access_required
def post_category_association(food_id, category_id):
    food = Food.query.filter_by(id=food_id).first()
    if not food:
        raise APIError(f"No food with id {food_id} exists", 404)
    category = FoodCategory.query.filter_by(id=category_id).first()
    if not category:
        raise APIError(f"No food with id {category_id} exists", 404)
    if category.id in [i.category.id for i in food.categories]:
        raise APIError(
            f"Category {category_id} is already linked to food {food_id}"
        )
    foodcategoryassociation = FoodCategoryAssociation(
        food_id=food.id, category_id=category.id
    )
    db.session.add(foodcategoryassociation)
    db.session.commit()
    json_obj = [category.category.to_dict() for category in food.categories]
    return jsonify(json_obj)


@bp.route("/foods/<food_id>/categories/<category_id>", methods=["DELETE"])
@login_required
# TODO ACCESS CONTROL
# @list_access_required
def delete_category(food_id, category_id):
    food = Food.query.filter_by(id=food_id).first()
    if not food:
        raise APIError(f"No food with id {food_id} exists", 404)
    category = FoodCategory.query.filter_by(id=category_id).first()
    if not category:
        raise APIError(f"No category with id {category_id} exists", 404)
    if category.id not in [i.category.id for i in food.categories]:
        raise APIError(
            f"Category {category_id} does not belong to Food {food_id}"
        )
    category_association = FoodCategoryAssociation.query.filter_by(
        food_id=food.id, category_id=category.id
    ).first()
    db.session.delete(category_association)
    db.session.commit()
    json_obj = [category.category.to_dict() for category in food.categories]
    return jsonify(json_obj)
