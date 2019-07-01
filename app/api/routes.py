import calendar
from flask import jsonify, request
from flask_login import login_user, current_user, logout_user
from app.models import (List, Entry, User, ListPermission,
                        Meal, Food, FoodCategory, FoodCategoryAssociation)
from app import db
from app.api import bp
from app.api.decorators import (list_access_required, entry_access_required,
                                list_owner_required, login_required)
from app.api.exceptions import APIError


def extract_args(args):
  offset = int(args.get('offset')) if 'offset' in args else 0
  limit = int(args.get('limit')) if 'limit' in args else None
  if limit and limit > 25:
    raise APIError('Limit cannot be over 25')
  start_today = bool(
      args.get('start_today')) if 'start_today' in args else False
  return dict(offset=offset, limit=limit, start_today=start_today)


@bp.route('/lists', methods=['GET'])
@login_required
def get_lists():
  args = extract_args(request.args)
  lists = current_user.get_lists()
  json_obj = [l.to_dict(args['offset'], args['limit'],
                        args['start_today']) for l in lists]
  return jsonify(json_obj), 200


@bp.route('/lists', methods=['POST'])
@login_required
def post_list():
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'listname' in req:
    raise APIError('listname is required')
  if req['listname'] == "":
    raise APIError('Listname cannot be empty')
  list_ = List(name=req['listname'])
  list_.generate_api_key()
  db.session.add(list_)
  db.session.commit()
  perm = ListPermission(
      list_id=list_.id, user_id=current_user.id, permission_level='owner')
  db.session.add(perm)
  db.session.commit()
  return jsonify(list_.to_dict()), 201


@bp.route('/lists/<list_id>', methods=['GET'])
@login_required
@list_access_required
def get_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id}', 404)
  return jsonify([list_.to_dict(args['offset'], args['limit'], args['start_today'])])


@bp.route('/lists/<list_id>', methods=['PATCH'])
@login_required
@list_access_required
def patch_list(list_id):
  args = extract_args(request.args)
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id}', 404)
  if 'listname' in req:
    list_.name = req['listname']
  db.session.commit()
  return jsonify([list_.to_dict(args['offset'], args['limit'], args['start_today'])])


@bp.route('/lists/<list_id>', methods=['DELETE'])
@login_required
@list_owner_required
@list_access_required
def delete_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  if list_:
    db.session.delete(list_)
    db.session.commit()
  lists = current_user.get_lists()
  json_obj = [l.to_dict(args['offset'], args['limit'],
                        args['start_today']) for l in lists]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/settings', methods=['PUT'])
@login_required
@list_access_required
def put_list_settings(list_id):
  args = extract_args(request.args)
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  list_ = List.query.filter_by(id=list_id).first()
  settings = list_.get_settings_for_user(current_user)
  # TODO functionize (start_day_of_week, days_to_display = extract_from_req(start_day_of_week, days_to_display))
  if not 'start_day_of_week' in req:
    raise APIError('start_day_of_week is required')
  if not 'days_to_display' in req:
    raise APIError('days_to_display is required')
  days_to_display = int(req['days_to_display'])
  if days_to_display < 5 and days_to_display > 21:
    raise APIError('days_to_display needs to be a number between 5-21')
  allowed_days = list(calendar.day_name)
  allowed_days.append("Today")
  start_day_of_week = req['start_day_of_week']
  if start_day_of_week not in allowed_days:
    raise APIError(
        f'start_day_of_week needs to be one of:  {" ".join(allowed_days)}')
  if start_day_of_week == "Today":
    start_day_of_week = -1
  else:
    start_day_of_week = allowed_days.index(start_day_of_week)
  settings.start_day_of_week = start_day_of_week
  settings.days_to_display = days_to_display
  db.session.commit()
  return jsonify([list_.to_dict(args['offset'], args['limit'], args['start_today'])])


@bp.route('/lists/<list_id>/shares', methods=['GET'])
@login_required
@list_access_required
def get_list_shares(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'List with id {list_id} not found', 404)
  return jsonify([i.to_dict() for i in list_.users])


@bp.route('/lists/<list_id>/shares', methods=['POST'])
@login_required
@list_access_required
@list_owner_required
def post_list_shares(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'List with id {list_id} not found', 404)
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if 'username' not in req:
    raise APIError('Username is required')
  user_ = User.query.filter_by(username=req['username']).first()
  if not user_:
    raise APIError(f"User {req['username']} does not exist", 404)
  if user_ in list_.get_users_with_access():
    raise APIError(f"User {req['username']} already has access to this list")
  new_perm = ListPermission(
      user_id=user_.id, list_id=list_.id, permission_level='member')
  db.session.add(new_perm)
  db.session.commit()
  return jsonify([i.to_dict() for i in list_.users])


@bp.route('/lists/<list_id>/shares/<share_id>', methods=['DELETE'])
@login_required
@list_access_required
@list_owner_required
def delete_share(list_id, share_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'List with id {list_id} not found', 404)
  share = ListPermission.query.filter_by(id=share_id, list_id=list_id).first()
  if not share:
    raise APIError(f'Share with id {share_id} not found', 404)
  db.session.delete(share)
  db.session.commit()
  return jsonify([i.to_dict() for i in list_.users])


@bp.route('/days', methods=['GET'])
@login_required
def get_days():
  args = extract_args(request.args)
  lists = current_user.get_lists()
  days = [
      l.get_or_create_days(args['offset'], args['limit'], args['start_today']) for l in lists
  ]
  json_obj_days = [day.to_dict() for sublist in days for day in sublist]
  return jsonify(json_obj_days)


@bp.route('/lists/<list_id>/days', methods=['GET'])
@login_required
@list_access_required
def get_days_by_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  days = list_.get_or_create_days(
      args['offset'], args['limit'], args['start_today'])
  json_obj = [{
      'day': d.day,
      'id': d.id,
      'entries': [e.id for e in d.get_or_create_entries()]
  } for d in days]
  return jsonify(json_obj)


@bp.route('/entries', methods=['GET'])
@login_required
def get_entries():
  args = extract_args(request.args)
  lists = current_user.get_lists()
  days = [l.get_or_create_days(args['offset'], args['limit'],
                               args['start_today']) for l in lists]
  entries = [d.get_or_create_entries() for sublist in days for d in sublist]
  json_obj_entries = [e.to_dict() for sublist in entries for e in sublist]
  return jsonify(json_obj_entries)


@bp.route('/entries/<entry_id>', methods=['PATCH'])
@login_required
@entry_access_required
def patch_entry(entry_id):
  # TODO functionize -> get_json -> check that there is content (or raise)
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  entry = Entry.query.filter_by(id=entry_id).first_or_404()
  entry.value = req['value']
  db.session.commit()
  return jsonify(entry.to_dict()), 201


@bp.route('/lists/<list_id>/entries', methods=['GET'])
@login_required
@list_access_required
def get_entries_by_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  days = list_.get_or_create_days(
      args['offset'], args['limit'], args['start_today'])
  entries = [e.get_or_create_entries() for e in days]
  json_obj = [e.to_dict() for sublist in entries for e in sublist]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/categories', methods=['GET'])
@login_required
@list_access_required
def get_categories_by_list(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id}')
  json_obj = [i.to_dict() for i in list_.categories]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/categories', methods=['POST'])
@login_required
@list_access_required
def post_categories(list_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'name' in req:
    raise APIError('name is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  if req['name'] in [i.name for i in list_.categories]:
    raise APIError(f'FoodCategory {req["name"]} already exists')
  foodcategory = FoodCategory(name=req['name'], list_id=list_id)
  db.session.add(foodcategory)
  db.session.commit()
  json_obj = [category.to_dict() for category in list_.categories]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/categories/<category_id>', methods=['DELETE'])
@login_required
@list_access_required
def delete_category_by_list(list_id, category_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  category = FoodCategory.query.filter_by(id=category_id).first()
  if not category:
    raise APIError(f'No category with id {category_id} exists', 404)
  db.session.delete(category)
  db.session.commit()
  json_obj = [category.to_dict() for category in list_.categories]
  return jsonify(json_obj)


@bp.route('/foods/<food_id>/categories', methods=['GET'])
@login_required
# TODO access control
# @list_access_required
def get_categories_by_food(food_id):
  food = Food.query.filter_by(id=food_id).first()
  if not food:
    raise APIError(f'No food with id {food_id} exists')
  json_obj = [category.category.to_dict() for category in food.categories]
  return jsonify(json_obj)


@bp.route('/foods/<food_id>/categories/<category_id>', methods=['POST'])
@login_required
# TODO access control
# @list_access_required
def post_category_association(food_id, category_id):
  food = Food.query.filter_by(id=food_id).first()
  if not food:
    raise APIError(f'No food with id {food_id} exists', 404)
  category = FoodCategory.query.filter_by(id=category_id).first()
  if not category:
    raise APIError(f'No food with id {category_id} exists', 404)
  if category.id in [i.category.id for i in food.categories]:
    raise APIError(
        f'Category {category_id} is already linked to food {food_id}')
  foodcategoryassociation = FoodCategoryAssociation(
      food_id=food.id, category_id=category.id)
  db.session.add(foodcategoryassociation)
  db.session.commit()
  json_obj = [category.category.to_dict() for category in food.categories]
  return jsonify(json_obj)


@bp.route('/foods/<food_id>/categories/<category_id>', methods=['DELETE'])
@login_required
# TODO ACCESS CONTROL
# @list_access_required
def delete_category(food_id, category_id):
  food = Food.query.filter_by(id=food_id).first()
  if not food:
    raise APIError(f'No food with id {food_id} exists', 404)
  category = FoodCategory.query.filter_by(id=category_id).first()
  if not category:
    raise APIError(f'No category with id {category_id} exists', 404)
  if category.id not in [i.category.id for i in food.categories]:
    raise APIError(f'Category {category_id} does not belong to Food {food_id}')
  category_association = FoodCategoryAssociation.query.filter_by(
      food_id=food.id, category_id=category.id).first()
  db.session.delete(category_association)
  db.session.commit()
  json_obj = [category.category.to_dict() for category in food.categories]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/foods', methods=['GET'])
@login_required
@list_access_required
def get_foods(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists')
  json_obj = [food.to_dict() for food in list_.foods]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/foods/<food_id>', methods=['PUT'])
@login_required
@list_access_required
def put_food(list_id, food_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'name' in req:
    raise APIError('name is required')
  if not 'categories' in req:
    raise APIError('categories is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  food = Food.query.filter_by(list_id=list_.id, id=food_id).first()
  if not food:
    raise APIError(f'No food with id {food_id} exists', 404)
  food.name = req['name']
  categories_to_associate = [
      i for i in list_.categories if i.name in req['categories']]
  categories_to_disassociate = [
      i for i in list_.categories if i.name not in req['categories']]
  categories_to_add = [i for i in req['categories']
                       if i not in [i.name for i in categories_to_associate]]
  for category in categories_to_add:
    fc = FoodCategory(list_id=list_.id, name=category)
    db.session.add(fc)
    db.session.commit()
    fca = FoodCategoryAssociation(category_id=fc.id, food_id=food.id)
    db.session.add(fca)
    db.session.commit()
  for category in categories_to_associate:
    if category.id not in [i.category.id for i in food.categories]:
      fca = FoodCategoryAssociation(category_id=category.id, food_id=food.id)
      db.session.add(fca)
  for category in categories_to_disassociate:
    if category.id in [i.category.id for i in food.categories]:
      fca = FoodCategoryAssociation.query.filter_by(category_id=category.id, food_id=food.id).first()
      db.session.delete(fca)
  db.session.commit()
  json_obj = [food.to_dict() for food in list_.foods]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/foods/<food_id>', methods=['DELETE'])
@login_required
@list_access_required
def delete_food(list_id, food_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  food = Food.query.filter_by(list_id=list_.id, id=food_id).first()
  if not food:
    raise APIError(f'No meal with id {food_id} exists', 404)
  db.session.delete(food)
  db.session.commit()
  json_obj = [food.to_dict() for food in list_.foods]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/foods', methods=['POST'])
@login_required
@list_access_required
def post_foods(list_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'name' in req:
    raise APIError('name is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  if Food.query.filter_by(name=req['name'], list_id=list_.id).first():
    raise APIError(f'Food {req["name"]} already exists')
  food = Food(list_id=list_.id, name=req['name'])
  db.session.add(food)
  db.session.commit()
  json_obj = [food.to_dict() for food in list_.foods]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/meals', methods=['GET'])
@login_required
@list_access_required
def get_meals(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists')
  json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/meals/<meal_id>', methods=['DELETE'])
@login_required
@list_access_required
def delete_meal(list_id, meal_id):
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  meal = Meal.query.filter_by(list_id=list_.id, id=meal_id).first()
  if not meal:
    raise APIError(f'No meal with id {meal_id} exists', 404)
  db.session.delete(meal)
  db.session.commit()
  json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/meals/<meal_id>', methods=['PATCH'])
@login_required
@list_access_required
def patch_meals(list_id, meal_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'name' in req:
    raise APIError('name is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  meal = Meal.query.filter_by(list_id=list_.id, id=meal_id).first()
  if not meal:
    raise APIError(f'No meal with id {meal_id} exists', 404)
  meal.name = req['name']
  db.session.commit()
  json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/meals', methods=['POST'])
@login_required
@list_access_required
def post_meals(list_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'name' in req:
    raise APIError('name is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  if Meal.query.filter_by(name=req['name'], list_id=list_.id).first():
    raise APIError(f'Meal {req["name"]} already exists')
  order = 1 + \
      max([i.order for i in Meal.query.filter_by(list_id=list_.id).all()])
  meal = Meal(list_id=list_.id, name=req['name'], order=order)
  db.session.add(meal)
  db.session.commit()
  json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
  return jsonify(json_obj)


@bp.route('/lists/<list_id>/meals', methods=['PUT'])
@login_required
@list_access_required
def put_meals(list_id):
  req = request.get_json()
  print(req)
  if not req:
    raise APIError('application/json is required')
  if not isinstance(req, list):
    raise APIError('A list of meals is required')
  # if not 'meals' in req:
  #   raise APIError('meals is required')
  list_ = List.query.filter_by(id=list_id).first()
  if not list_:
    raise APIError(f'No list with id {list_id} exists', 404)
  meals = Meal.query.filter_by(list_id=list_.id).all()
  # verify integrity of received list
  for meal in req:
    if 'id' in meal:
      if not meal['id'] in [i.id for i in meals]:
        raise APIError('ID reassignment is not allowed')
    if not 'name' in meal:
      raise APIError(f'No name received in {meal}')
  for meal in meals:
    if meal.id not in [i['id'] for i in req if 'id' in i]:
      db.session.delete(meal)
  db.session.commit()
  meals = Meal.query.filter_by(list_id=list_.id).all()
  for index, req_meal in enumerate(req):
    if 'id' in req_meal and req_meal['id'] in [i.id for i in meals]:
      meals_index = [i.id for i in meals].index(req_meal['id'])
      meals[meals_index].order = index
      meals[meals_index].name = req_meal['name']
    else:
      new_meal = Meal(list_id=list_.id, name=req_meal['name'], order=index)
      db.session.add(new_meal)
  db.session.commit()
  json_obj = [meal.to_dict() for meal in list_.get_or_create_meals()]
  return jsonify(json_obj)


@bp.route('/users', methods=['GET'])
@login_required
def get_users():
  users = User.query.all()
  users = [i.to_dict() for i in users]
  return jsonify(users), 200


@bp.route('/users', methods=['POST'])
def register():
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  if not 'username' in req:
    raise APIError('username is required')
  if not 'email' in req:
    raise APIError('email is required')
  if not 'firstname' in req:
    raise APIError('firstname is required')
  if not 'lastname' in req:
    raise APIError('lastname is required')
  if User.query.filter_by(username=req['username']).first():
    raise APIError('Username already taken')
  if User.query.filter_by(email=req['email']).first():
    raise APIError('Email already taken')
  if len(req['password']) < 8:
    raise APIError('Password is too short, please use 8 characters or more')
  u = User(
      username=req['username'],
      email=req['email'],
      firstname=req['firstname'],
      lastname=req['lastname'],
      is_confirmed=False
  )
  u.set_password(req['password'])
  db.session.add(u)
  db.session.commit()
  # TODO confirm email
  # token = generate_confirmation_token(u.email)
  # confirm_url = url_for('auth.confirm_email', token=token, _external=True)
  # send_user_confirmation_email(u, confirm_url)
  login_user(u)
  return jsonify({'msg': 'Registered successfully', **u.to_dict()}), 201


@bp.route('/users/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
  user_ = User.query.filter_by(id=user_id).first()
  if user_ and user_ == current_user:
    db.session.delete(user_)
    db.session.commit()
  logout_user()
  return jsonify({'msg': 'User deleted'}), 401


@bp.route('/users/<user_id>', methods=['PUT'])
def put_users(user_id):
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  user_ = User.query.filter_by(id=user_id).first()
  if not user_:
    raise APIError(f'User with id {user_id} not found', 404)
  if not user_ == current_user:
    raise APIError('Insufficient permissions', 403)
  if not 'username' in req:
    raise APIError('username is required')
  if not 'email' in req:
    raise APIError('email is required')
  if not 'firstname' in req:
    raise APIError('firstname is required')
  if not 'lastname' in req:
    raise APIError('lastname is required')
  if 'password' in req and req['password'] != '':
    if len(req['password']) < 8:
      raise APIError('Password is too short, please use 8 characters or more')
    else:
      current_user.set_password(req['password'])
  if req['username'] != current_user.username:
    if User.query.filter_by(username=req['username']).first():
      raise APIError('Username already taken')
    current_user.username = req['username']
  if req['email'] != current_user.email:
    if User.query.filter_by(email=req['email']).first():
      raise APIError('Email already taken')
    current_user.email = req['email']
  # TODO confirm email
  # token = generate_confirmation_token(u.email)
  # confirm_url = url_for('auth.confirm_email', token=token, _external=True)
  # send_user_confirmation_email(u, confirm_url)
  if req['firstname'] != current_user.firstname:
    current_user.firstname = req['firstname']
  if req['lastname'] != current_user.lastname:
    current_user.lastname = req['lastname']
  db.session.commit()
  return jsonify({'msg': 'User updated successfully', **current_user.to_dict()}), 201

######################
###                ###
### Authentication ###
###                ###
######################


@bp.route('/auth/login', methods=['POST'])
def login():
  req = request.get_json()
  if not req:
    raise APIError('application/json is required')
  u = User.query.filter_by(username=req['username']).first()
  if u is None or not u.check_password(req['password']):
    raise APIError('Invalid username or password!', 401)
  login_user(u)
  return jsonify({'msg': 'Logged in successfully', **u.to_dict()}), 200


@bp.route('/auth/user', methods=['GET'])
def user():
  if current_user.is_authenticated:
    return jsonify({'msg': 'Session still valid', **current_user.to_dict()}), 200
  raise APIError('Please log in', 401)


@bp.route('/auth/logout')
@login_required
def logout():
  logout_user()
  return jsonify({'msg': 'Logged out successfully'}), 200
