from time import time
from datetime import date, timedelta
from os import urandom
from binascii import b2a_hex
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from flask import current_app
from app import db, login

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
  default_list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  lists = db.relationship("List", foreign_keys='List.owner_id')
  own_shares = db.relationship("Share", foreign_keys='Share.owner_id')
  shared_with = db.relationship("Share", foreign_keys='Share.grantee_id')

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
    except:
      return
    return User.query.get(uid)

  def get_lists(self):
    lists = self.lists
    lists += [i.get_list() for i in self.shared_with if i.owner_id != self.id]
    return lists


class List(db.Model):
  __tablename__ = 'list'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(250))
  apikey = db.Column(db.String(250))
  last_updated = db.Column(db.DateTime)
  entries_per_day = db.Column(db.Integer)
  entry_names = db.Column(db.String(250), default='Lunch,Dinner')

  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  days = db.relationship("Day")
  shares = db.relationship("Share")
  settings = db.relationship("ListSettings")

  def __repr__(self):
    return "<List {}>".format(self.name)

  def generate_api_key(self):
    self.apikey = str(b2a_hex(urandom(16)), 'utf-8')
    return self.apikey

  def get_users_with_access(self):
    accessers = [i.id for i in self.shares]
    accessers.append(self.owner_id)
    return accessers

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


class Day(db.Model):
  __tablename__ = 'day'
  id = db.Column(db.Integer, primary_key=True)
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  list_ = db.relationship("List", backref="List")
  day = db.Column(db.Date)
  entries = db.relationship("Entry")

  def __repr__(self):
    return "<Day {} of List {}>".format(self.day, self.list_.name)

  def get_entries(self):
    entry_names = self.list_.entry_names.split(',')
    for i in entry_names:
      entry = Entry.query.filter_by(day_id=self.id, key=i).first()
      if not entry:
        entry = Entry(day_id=self.id, key=i, value='Empty')
        db.session.add(entry)
        db.session.commit()
    return self.entries


class ListSettings(db.Model):
  __tablename__ = 'listsettings'
  id = db.Column(db.Integer, primary_key=True)
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  start_day_of_week = db.Column(db.Integer, default=None)
  days_to_display = db.Column(db.Integer, default=7)


class Entry(db.Model):
  __tablename__ = 'entry'
  id = db.Column(db.Integer, primary_key=True)
  day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
  day = db.relationship("Day", backref="Day")
  key = db.Column(db.String(256))
  value = db.Column(db.String(256))

  def __repr__(self):
    return "<Entry {} of List {}>".format(self.id, self.day.day)


class Share(db.Model):
  __tablename__ = 'shares'
  id = db.Column(db.Integer, primary_key=True)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  grantee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))

  def get_list(self):
    return List.query.filter_by(id=self.list_id).first()
