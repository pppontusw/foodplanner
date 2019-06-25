from flask import jsonify, request
from flask_login import login_user, current_user, logout_user
from app.models import List, Entry, User, ListPermission
from app import db
from app.api import bp
from app.api.decorators import list_access_required, entry_access_required, list_owner_required, login_required


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


@bp.route('/lists/<lid>', methods=['GET'])
@login_required
@list_access_required
def get_list(lid):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=lid).first()
  return jsonify([list_.to_dict(args['offset'], args['limit'], args['start_today'])])


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


@bp.route('/lists/<lid>/days', methods=['GET'])
@login_required
@list_access_required
def get_days_by_list(lid):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=lid).first()
  days = list_.get_days(args['offset'], args['limit'], args['start_today'])
  json_obj = [{
      'day': d.day,
      'id': d.id,
      'entries': [e.id for e in d.get_entries()]
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


@bp.route('/lists/<lid>/entries', methods=['GET'])
@login_required
@list_access_required
def get_entries_by_list(lid):
  args = extract_args(request.args)
  list_ = List.query.filter_by(id=lid).first()
  days = list_.get_days(args['offset'], args['limit'], args['start_today'])
  entries = [e.entries for e in days]
  json_obj = [e.to_dict() for sublist in entries for e in sublist]
  return jsonify(json_obj)


@bp.route('/lists', methods=['POST'])
@login_required
def post_list():
  req = request.get_json()
  if req['listname'] == "":
    return jsonify({'msg': 'Listname cannot be empty'}), 400
  list_ = List(name=req['listname'])
  list_.generate_api_key()
  db.session.add(list_)
  db.session.commit()
  perm = ListPermission(
      list_id=list_.id, user_id=current_user.id, permission_level='owner')
  db.session.add(perm)
  db.session.commit()
  return jsonify(list_.to_dict()), 201


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
    return jsonify({'msg': 'Invalid username or password!'}), 401
  login_user(u)
  return jsonify({'msg': 'Login successful',
                  'user': u.username}), 200


@bp.route('/auth/user', methods=['GET'])
def user():
  if current_user.is_authenticated:
    return jsonify({'msg': 'Session still valid', 'user': current_user.username}), 200
  return jsonify({'msg': 'Please log in'}), 401


@bp.route('/auth/logout')
@login_required
def logout():
  logout_user()
  return jsonify({'msg': 'Logged out successfully'}), 200


@bp.route('/auth/register', methods=['POST'])
def register():
  req = request.get_json()
  if User.query.filter_by(username=req['username']).first():
    return jsonify({'msg': 'Username already taken!'}), 400
  if User.query.filter_by(email=req['email']).first():
    return jsonify({'msg': 'Email already taken!'}), 400
  if len(req['password']) < 8:
    return jsonify({'msg': 'Password is too short, please use 8 characters or more'}), 400
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
  return jsonify({'msg': 'Registered successfully',
                  'user': u.username}), 200
