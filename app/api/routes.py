import calendar
from flask import jsonify, request
from flask_login import login_user, current_user, logout_user
from app.models import List, Entry, User, ListPermission
from app import db
from app.api import bp
from app.api.decorators import list_access_required, entry_access_required, list_owner_required, login_required
from app.api.exceptions import APIError


def extract_args(args):
  offset = int(args.get('offset')) if 'offset' in args else 0
  limit = int(args.get('limit')) if 'limit' in args else None
  start_today = bool(
      args.get('start_today')) if 'start_today' in args else False
  return dict(offset=offset, limit=limit, start_today=start_today)


@bp.route('/entries/<entry_id>', methods=['PUT'])
@login_required
@entry_access_required
def put_entry(entry_id):
  req = request.get_json()
  entry = Entry.query.filter_by(id=entry_id).first_or_404()
  entry.value = req['value']
  db.session.commit()
  return jsonify(entry.to_dict()), 201


@bp.route('/lists', methods=['GET'])
@login_required
def get_lists():
  args = extract_args(request.args)
  lists = current_user.get_lists()
  json_obj = [l.to_dict(args['offset'], args['limit'],
                        args['start_today']) for l in lists]
  return jsonify(json_obj), 200


@bp.route('/lists/<list_id>', methods=['GET'])
@login_required
@list_access_required
def get_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  return jsonify([list_.to_dict(args['offset'], args['limit'], args['start_today'])])


@bp.route('/lists/<list_id>/settings', methods=['PUT'])
@login_required
@list_access_required
def put_list_settings(list_id):
  args = extract_args(request.args)
  req = request.get_json()
  list_ = List.query.filter_by(id=list_id).first()
  settings = list_.get_settings_for_user(current_user)
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
      l.get_days(args['offset'], args['limit'], args['start_today']) for l in lists
  ]
  json_obj_days = [day.to_dict() for sublist in days for day in sublist]
  return jsonify(json_obj_days)


@bp.route('/lists/<list_id>/days', methods=['GET'])
@login_required
@list_access_required
def get_days_by_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  days = list_.get_days(args['offset'], args['limit'], args['start_today'])
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
  days = [l.get_days(args['offset'], args['limit'],
                     args['start_today']) for l in lists]
  entries = [e.entries for sublist in days for e in sublist]
  json_obj_entries = [e.to_dict() for sublist in entries for e in sublist]
  return jsonify(json_obj_entries)


@bp.route('/lists/<list_id>/entries', methods=['GET'])
@login_required
@list_access_required
def get_entries_by_list(list_id):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=list_id).first()
  days = list_.get_days(args['offset'], args['limit'], args['start_today'])
  entries = [e.entries for e in days]
  json_obj = [e.to_dict() for sublist in entries for e in sublist]
  return jsonify(json_obj)


@bp.route('/lists', methods=['POST'])
@login_required
def post_list():
  req = request.get_json()
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


@bp.route('/users', methods=['GET'])
# @login_required
# TODO admin required ?
def get_users():
  users = User.query.all()
  users = [i.to_dict() for i in users]
  return jsonify(users), 200


@bp.route('/users', methods=['POST'])
def register():
  req = request.get_json()
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


@bp.route('/users/<user_id>', methods=['PUT'])
def put_user(user_id):
  req = request.get_json()
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
