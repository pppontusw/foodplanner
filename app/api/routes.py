from datetime import date
from flask import jsonify, request, g
from flask_login import login_user, current_user, logout_user
from app.models import List, Entry, User, ListPermission
from app import db
from app.api import bp
from app.api.decorators import list_access_required, entry_access_required, list_owner_required, login_required

def get_dict_from_list(l, start_day=0, end_day=7):
  days = l.get_days(start_day, end_day)
  lsettings = l.get_settings_for_user(current_user)
  listdict = {
      'name': l.name,
      'id': l.id,
      'days': [
          {'day': d.day.strftime('%Y-%m-%dT%H:%M:%SZ'),
           'id': d.id,
           'entries': [
               {'meal': e.key,
                'value': e.value,
                'id': e.id
                } for e in d.get_entries()]
          } for d in days
      ],
      'settings': {
          'start_day_of_week': lsettings.start_day_of_week,
          'days_to_display': lsettings.days_to_display
      },
      'shares': [i.user.username for i in l.users]
  }
  return listdict

def get_previous_of_weekday(d):
  weekday = d - date.today().weekday()
  if weekday > 0:
    weekday -= 7
  return weekday


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


@bp.route('/update/<entry_id>', methods=['POST'])
@login_required
@entry_access_required
def api_update(entry_id):
  req = request.get_json()
  entry = Entry.query.filter_by(id=entry_id).first_or_404()
  entry.value = req['value']
  db.session.commit()
  return jsonify({'message': 'OK!'}), 201


@bp.route('/lists', methods=['GET'])
@login_required
def get_lists():
  lists = current_user.get_lists()
  json_obj = [get_dict_from_list(l, 0, 4) for l in lists]
  return jsonify(json_obj), 200


@bp.route('/list/<lid>', methods=['GET'])
@login_required
@list_access_required
def get_list(lid):
  list_ = List.query.filter_by(id=lid).first()
  sett = list_.get_settings_for_user(current_user)
  if sett.start_day_of_week != -1:
    d = get_previous_of_weekday(sett.start_day_of_week)
  else:
    d = 0
  json_obj = get_dict_from_list(list_, d, d + sett.days_to_display)
  return jsonify(json_obj)

# TODO probably remove
# @bp.route('/list_settings/<lid>', methods=['GET'])
# @login_required
# @list_access_required
# def get_list_settings(lid):
#   list_ = List.query.filter_by(id=lid).first()
#   lsettings = list_.get_settings_for_user(current_user)
#   json_obj = dict(
#       settings=dict(
#           start_day_of_week=lsettings.start_day_of_week,
#           days_to_display=lsettings.days_to_display
#       ),
#       shares=[i.user.username for i in list_.users]
#   )
#   return jsonify(json_obj)

@bp.route('/new_list', methods=['POST'])
@login_required
def new_list():
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
  json_obj = get_dict_from_list(list_, 0, 4)
  return jsonify(json_obj), 201


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
