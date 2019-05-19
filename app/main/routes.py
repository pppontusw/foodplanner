from datetime import date
from flask import render_template, redirect, url_for, jsonify, request, flash
from flask_login import current_user, login_required
from app.models import List, Entry, User, ListPermission
from app import db
from app.main import bp
from app.main.decorators import check_list_access, check_entry_access, check_list_owner
from app.main.forms import NewListForm, ConfirmDeleteForm, ListSettingsForm, ShareForm

def get_previous_of_weekday(d):
  weekday = d - date.today().weekday()
  if weekday > 0:
    weekday -= 7
  return weekday

@bp.route('/index')
@bp.route('/')
@login_required
def index():
  if current_user.is_authenticated:
    return redirect(url_for('main.get_lists'))
  return render_template('index.html')


@bp.route('/delete_list/<list_id>', methods=['GET', 'POST'])
@login_required
@check_list_owner
def delete_list(list_id):
  list_ = List.query.filter_by(id=list_id).first_or_404()
  form = ConfirmDeleteForm()
  if form.validate_on_submit():
    if 'yes' in request.form:
      list_.delete_list()
      flash('List deleted successfully!', 'success')
      return redirect(url_for('main.index'))
    else:
      return redirect(url_for('main.index'))
  return render_template('confirm_delete.html', form=form, list_=list_)


@bp.route('/get_api_key/<list_id>')
@login_required
@check_list_access
def get_api_key(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  return render_template('get_api_key.html', list_=list_)


@bp.route('/lists')
@login_required
def get_lists():
  lists = current_user.get_lists()
  return render_template('lists.html', lists=lists)


@bp.route('/list/<list_id>')
@login_required
@check_list_access
def get_list(list_id):
  list_ = List.query.filter_by(id=list_id).first_or_404()
  sett = list_.get_settings_for_user(current_user)
  if sett.start_day_of_week != -1:
    d = get_previous_of_weekday(sett.start_day_of_week)
  else:
    d = 0
  days = list_.get_days(
      d,
      d + sett.days_to_display
  )
  return render_template('list.html', list_=list_, days=days)


@bp.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
  form = NewListForm()
  if form.validate_on_submit():
    list_ = List(name=form.name.data)
    list_.generate_api_key()
    db.session.add(list_)
    db.session.commit()
    perm = ListPermission(list_id=list_.id, user_id=current_user.id, permission_level='owner')
    db.session.add(perm)
    db.session.commit()
    return redirect(url_for('main.get_list', list_id=list_.id))
  return render_template('new_list.html', form=form)


@bp.route('/settings/<list_id>')
@login_required
@check_list_access
def settings(list_id):
  return redirect(url_for('main.list_settings', list_id=list_id))


@bp.route('/list_settings/<list_id>', methods=['GET', 'POST'])
@login_required
@check_list_access
def list_settings(list_id):
  form = ListSettingsForm()
  list_ = List.query.filter_by(id=list_id).first_or_404()
  curr_settings = list_.get_settings_for_user(current_user)
  if request.method == 'GET':
    form.name.data = list_.name
    form.daysToDisplay.data = curr_settings.days_to_display
    form.startDayOfTheWeek.data = curr_settings.start_day_of_week
  if form.validate_on_submit():
    if list_.name != form.name.data:
      list_.name = form.name.data
    if curr_settings.start_day_of_week != form.startDayOfTheWeek.data:
      curr_settings.start_day_of_week = form.startDayOfTheWeek.data
    if curr_settings.days_to_display != form.daysToDisplay.data:
      curr_settings.days_to_display = form.daysToDisplay.data
    db.session.commit()
  return render_template('list_settings.html', list_=list_, form=form)


@bp.route('/list_foods/<list_id>')
@login_required
@check_list_access
def list_foods(list_id):
  # TODO Create a list of meals that can be autocompleted
  list_ = List.query.filter_by(id=list_id).first_or_404()
  return render_template('list_foods.html', list_=list_)


@bp.route('/list_daily_meals/<list_id>')
@login_required
@check_list_access
def list_daily_meals(list_id):
  # TODO List and change the different meals of the day i.e. lunch, dinner, breakfast etc.
  list_ = List.query.filter_by(id=list_id).first_or_404()
  return render_template('list_daily_meals.html', list_=list_)


@bp.route('/drop_share/<list_id>/<user_id>')
@login_required
@check_list_access
def drop_share(list_id, user_id):
  s = ListPermission.query.filter_by(user_id=user_id, list_id=list_id).first()
  if s.permission_level != 'owner':
    db.session.delete(s)
    db.session.commit()
  return redirect(url_for('main.list_shares', list_id=list_id))


@bp.route('/list_shares/<list_id>', methods=['GET', 'POST'])
@login_required
@check_list_access
def list_shares(list_id):
  form = ShareForm()
  list_ = List.query.filter_by(id=list_id).first_or_404()
  l_shares = list_.users
  if form.validate_on_submit():
    u = User.query.filter(
        (User.username == form.target.data.lower()) | (User.email == form.target.data.lower())
    ).first()
    s = ListPermission.query.filter_by(
        list_id=list_.id, user_id=u.id
    ).first()
    if not s:
      s = ListPermission(list_id=list_.id, user_id=u.id, permission_level='rw')
      db.session.add(s)
      db.session.commit()
    return redirect(url_for('main.list_shares', list_id=list_.id))
  return render_template('list_shares.html',
                         list_=list_,
                         form=form,
                         list_shares=l_shares
                        )




@bp.route('/api/update/<entry_id>', methods=['POST'])
@login_required
@check_entry_access
def api_update(entry_id):
  entry = Entry.query.filter_by(id=entry_id).first_or_404()
  entry.value = request.form.get('value', 'Emtpy')
  db.session.commit()
  return jsonify({'message': 'OK!'})
