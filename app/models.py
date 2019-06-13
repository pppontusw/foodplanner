from time import time
from datetime import date, timedelta
from os import urandom
from binascii import b2a_hex
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from flask import current_app
from app import db, login
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

@login.user_loader
def load_user(uid):
  return User.query.get(int(uid))

class User(UserMixin, db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(250), nullable=False)
  email = db.Column(db.String(250), nullable=False)
  firstname = db.Column(db.String(250))
  lastname = db.Column(db.String(250))
  password = db.Column(db.String(250))
  is_confirmed = db.Column(db.Boolean)
  is_admin = db.Column(db.Boolean, default=False)

  lists = db.relationship("ListPermission", back_populates='user')

  def __repr__(self):
    return "<User {}>".format(self.email)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)

  def get_reset_password_token(self, expires_in=600):
    return jwt.encode(
        {'reset_password': self.id, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  @staticmethod
  def verify_reset_password_token(token):
    try:
      uid = jwt.decode(token, current_app.config['SECRET_KEY'],
                       algorithms=['HS256'])['reset_password']
    except jwt.PyJWTError:  # any exception in this method should result in failure
      return
    return User.query.get(uid)

  def get_lists(self):
    return [i.list_ for i in self.lists]

  def delete_user(self):
    lists = self.get_lists()
    for list_ in lists:
      if list_ is not None:
        days = list_.days
        for day in days:
          entries = day.entries
          for entry in entries:
            db.session.delete(entry)
          db.session.delete(day)
        for sett in list_.settings:
          db.session.delete(sett)
        for lpm in list_.users:
          db.session.delete(lpm)
        db.session.delete(list_)
    db.session.delete(self)
    db.session.commit()


class List(db.Model):
  __tablename__ = 'list'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(250))
  apikey = db.Column(db.String(250))
  last_updated = db.Column(db.DateTime)
  entries_per_day = db.Column(db.Integer)
  entry_names = db.Column(db.String(250), default='Lunch,Dinner')

  users = db.relationship("ListPermission", back_populates='list_')
  days = db.relationship("Day")
  settings = db.relationship("ListSettings")

  def __repr__(self):
    return "<List {}>".format(self.name)

  def generate_api_key(self):
    self.apikey = str(b2a_hex(urandom(16)), 'utf-8')
    return self.apikey

  def get_users_with_access(self):
    return [i.user for i in self.users]

  def get_non_owners(self):
    return [i.user for i in self.users if i.permission_level == 'rw']

  def get_owners(self):
    return [i.user for i in self.users if i.permission_level == 'owner']

  def get_days(self, start=0, end=7):
    now = date.today()
    days = []
    for i in range(start, end):
      delta = timedelta(days=i)
      day = Day.query.filter_by(day=now+delta, list_id=self.id).first()
      if not day:
        day = Day(list_id=self.id, day=now+delta)
        db.session.add(day)
        db.session.commit()
      days.append(day)
    return days

  def get_settings_for_user(self, user):
    settings = ListSettings.query.filter_by(list_id=self.id, user_id=user.id).first()
    if not settings:
      settings = ListSettings(
          list_id=self.id,
          user_id=user.id,
          start_day_of_week=-1
      )
      db.session.add(settings)
      db.session.commit()
    return settings

  def delete_list(self):
    days = self.days
    for day in days:
      entries = day.entries
      for entry in entries:
        db.session.delete(entry)
      db.session.delete(day)
    for sett in self.settings:
      db.session.delete(sett)
    for userperm in self.users:
      db.session.delete(userperm)
    db.session.delete(self)
    db.session.commit()


class ListSettings(db.Model):
  __tablename__ = 'listsettings'
  id = db.Column(db.Integer, primary_key=True)
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  start_day_of_week = db.Column(db.Integer, default=-1)
  days_to_display = db.Column(db.Integer, default=7)

  user = db.relationship("User")
  list_ = db.relationship("List")

  def __repr__(self):
    return "<ListSettings {} of List {} for User {}>".format(
        self.id, self.list_.name, self.user.username
    )


class Day(db.Model):
  __tablename__ = 'day'
  id = db.Column(db.Integer, primary_key=True)
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  day = db.Column(db.Date)

  list_ = db.relationship("List", back_populates='days')
  entries = db.relationship("Entry")

  def __repr__(self):
    return "<Day {} of List {}>".format(self.day, self.list_.name)

  def get_entries(self):
    entry_names = self.list_.entry_names.split(',')
    for i in entry_names:
      entry = Entry.query.filter_by(day_id=self.id, key=i).first()
      if not entry:
        entry = Entry(day_id=self.id, key=i, value='')
        db.session.add(entry)
        db.session.commit()
    return self.entries


class Entry(db.Model):
  __tablename__ = 'entry'
  id = db.Column(db.Integer, primary_key=True)
  day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
  key = db.Column(db.String(256))
  value = db.Column(db.String(256))

  day = db.relationship("Day", back_populates='entries')

  def __repr__(self):
    return "<Entry {} of Day {} in List {}>".format(self.id, self.day.day, self.day.list_.name)


class ListPermission(db.Model):
  __tablename__ = 'listpermission'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  permission_level = db.Column(db.String(256))

  list_ = db.relationship("List", back_populates='users')
  user = db.relationship("User", back_populates='lists')

  def __repr__(self):
    return "<ListPermission {} of List {} to User {} at level {}>".format(
        self.id, self.list_.name, self.user.username, self.permission_level
    )
