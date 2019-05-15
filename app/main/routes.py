from flask import render_template, redirect, url_for, jsonify, request, flash
from flask_login import current_user, login_required
from app.models import List, Entry
from app import db
from app.main import bp
from app.main.decorators import check_list_access, check_entry_access
from app.main.forms import NewListForm, ConfirmDeleteForm, ListSettingsForm

@bp.route('/index')
@bp.route('/')
@login_required
def index():
  if current_user.is_authenticated:
    return redirect(url_for('main.get_lists'))
  return render_template('index.html')


@bp.route('/delete_list/<list_id>', methods=['GET', 'POST'])
@login_required
@check_list_access
# TODO @check_list_owner
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
  return render_template('confirm_delete.html', form=form, list=list_)


@bp.route('/get_api_key/<list_id>')
@login_required
@check_list_access
def get_api_key(list_id):
  list_ = List.query.filter_by(id=list_id).first()
  return render_template('get_api_key.html', list=list_)


@bp.route('/lists')
@login_required
def get_lists():
  lists = List.query.filter_by(owner_id=current_user.id).all()
  return render_template('lists.html', lists=lists)


@bp.route('/list/<list_id>')
@login_required
@check_list_access
def get_list(list_id):
  list_ = List.query.filter_by(id=list_id).first_or_404()
  days = list_.get_days()
  return render_template('list.html', list=list_, days=days)


@bp.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
  form = NewListForm()
  if form.validate_on_submit():
    list_ = List(name=form.name.data, owner_id=current_user.id)
    list_.generate_api_key()
    db.session.add(list_)
    db.session.commit()
    return redirect(url_for('main.get_list', list_id=list_.id))
  return render_template('new_list.html', form=form)


@bp.route('/settings/<list_id>')
@login_required
@check_list_access
def settings(list_id):
  # TODO TESTS
  return redirect(url_for('main.list_settings', list_id=list_id))


@bp.route('/list_settings/<list_id>', methods=['GET', 'POST'])
@login_required
@check_list_access
def list_settings(list_id):
  # TODO TESTS
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
  return render_template('list_settings.html', list=list_, form=form)


@bp.route('/list_foods/<list_id>')
@login_required
@check_list_access
def list_foods(list_id):
  # TODO TESTS
  list_ = List.query.filter_by(id=list_id).first_or_404()
  return render_template('list_foods.html', list=list_)


@bp.route('/list_daily_meals/<list_id>')
@login_required
@check_list_access
def list_daily_meals(list_id):
  # TODO TESTS
  list_ = List.query.filter_by(id=list_id).first_or_404()
  return render_template('list_daily_meals.html', list=list_)


@bp.route('/list_shares/<list_id>')
@login_required
@check_list_access
def list_shares(list_id):
  # TODO TESTS
  list_ = List.query.filter_by(id=list_id).first_or_404()
  return render_template('list_shares.html', list=list_)




@bp.route('/api/update/<entry_id>', methods=['POST'])
@login_required
@check_entry_access
def api_update(entry_id):
  entry = Entry.query.filter_by(id=entry_id).first_or_404()
  entry.value = request.form.get('value', 'Emtpy')
  db.session.commit()
  return jsonify({'message': 'OK!'})
