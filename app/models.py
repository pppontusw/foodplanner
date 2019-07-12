from time import time
from datetime import date, timedelta
from os import urandom
from binascii import b2a_hex
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import jwt
from sqlalchemy.exc import IntegrityError
from flask import current_app
from app import db, login


@login.user_loader
def load_user(uid):
    return User.query.get(int(uid))


class User(UserMixin, db.Model):
    """A foodplanner user"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    password = db.Column(db.String(250))
    is_confirmed = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean, default=False)

    # backref -> lists

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

    def to_dict(self):
        base = {
            'id': self.id,
            'username': self.username
        }
        privileged = {
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname
        }
        if self == current_user:
            return {**base, **privileged}
        return base


class List(db.Model):
    """
    A list containst days, settings, and other related items

    Takes name (apikey, last_updated)
    """
    __tablename__ = 'list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    apikey = db.Column(db.String(250))
    last_updated = db.Column(db.DateTime)

    # backref users -> ListPermission (assoc table)

    # backref days -> Day

    # backref settings -> ListSettings

    # backref meals -> Meal

    # backref foods -> Food

    def __repr__(self):
        return "<List {}>".format(self.name)

    def generate_api_key(self):
        self.apikey = str(b2a_hex(urandom(16)), 'utf-8')
        return self.apikey

    def get_users_with_access(self):
        return [i.user for i in self.users]

    def get_non_owners(self):
        return [i.user for i in self.users if i.permission_level == 'member']

    def get_owners(self):
        return [i.user for i in self.users if i.permission_level == 'owner']

    def get_or_create_days(self, offset=0, limit=None, start_today=False):
        now = date.today()
        list_settings = self.get_settings_for_user(current_user)
        days = []
        days_to_display = limit if limit else list_settings.days_to_display
        start_day = 0 if start_today else self.get_start_day()
        end_day = start_day + days_to_display + (offset * days_to_display)
        start_day += (offset * days_to_display)
        for i in range(start_day, end_day):
            delta = timedelta(days=i)
            day = Day.query.filter_by(day=now+delta, list_id=self.id).first()
            if not day:
                day = Day(list_id=self.id, day=now+delta)
                try:
                    db.session.add(day)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    # IT'S BEEN CREATED
                    day = Day.query.filter_by(
                        day=now+delta, list_id=self.id).first()
            days.append(day)
        return days

    def get_settings_for_user(self, user):
        settings = ListSettings.query.filter_by(
            list_id=self.id, user_id=user.id).first()
        if not settings:
            settings = ListSettings(
                list_id=self.id,
                user_id=user.id,
                start_day_of_week=-1
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    def get_or_create_meals(self):
        if not Meal.query.filter_by(list_id=self.id).first():
            for idx, i in enumerate(["Lunch", "Dinner"]):
                meal = Meal(list_id=self.id, name=i, order=idx)
                try:
                    db.session.add(meal)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
        return sorted(self.meals, key=lambda x: x.order)

    def to_dict(self, offset=0, limit=None, start_today=False):
        list_settings = self.get_settings_for_user(current_user)
        days = self.get_or_create_days(offset, limit, start_today)
        listdict = {
            'name': self.name,
            'id': self.id,
            'days': [
                d.id for d in days
            ],
            'settings': {
                'start_day_of_week': List.get_weekday_from_int(list_settings.start_day_of_week),
                'days_to_display': list_settings.days_to_display
            },
            'shares': [i.id for i in self.users],
            'is_owner': current_user in self.get_owners(),
            'meals': [i.id for i in self.get_or_create_meals()],
            'foods': [i.id for i in self.foods],
            'categories': [i.id for i in self.categories]
        }
        return listdict

    @staticmethod
    def get_previous_of_weekday(d):
        weekday = d - date.today().weekday()
        if weekday > 0:
            weekday -= 7
        return weekday

    @staticmethod
    def get_weekday_from_int(int_):
        if int_ == -1:
            return "Today"
        if (int_ < 0 or int_ > 6):
            raise ValueError("This integer cannot represent a weekday")
        days = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
        return days[int_]

    def get_start_day(self):
        list_settings = self.get_settings_for_user(current_user)
        if list_settings.start_day_of_week != -1:
            d = List.get_previous_of_weekday(list_settings.start_day_of_week)
        else:
            d = 0
        return d


class FoodCategory(db.Model):
    """
    Category of a Food

    A food can have many categories and a category can contain many foods
    """
    __tablename__ = 'foodcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete="CASCADE"), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('categories', passive_deletes=True))

    def __repr__(self):
        return "<FoodCategory {} of List {}>".format(
            self.name, self.list_.name
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class FoodCategoryAssociation(db.Model):
    """
    Joins foods and categories
    """
    __tablename__ = 'foodcategoryassociation'
    id = db.Column(db.Integer, primary_key=True)

    food_id = db.Column(db.Integer, db.ForeignKey(
        'foods.id', ondelete='CASCADE'), nullable=False)
    foods = db.relationship(
        "Food", backref=db.backref('categories', cascade="all", passive_deletes=True))

    category_id = db.Column(db.Integer, db.ForeignKey(
        'foodcategories.id', ondelete='CASCADE'), nullable=False)
    category = db.relationship(
        "FoodCategory", backref=db.backref('foods', cascade="all", passive_deletes=True))


class Food(db.Model):
    """
    A food will be suggested in the autocomplete for entries

    Takes list_id and name
    """
    __tablename__ = 'foods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete="CASCADE"), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('foods', passive_deletes=True))

    # backref ingredients -> Ingredient

    # backref categories -> FoodCategoryAssociation

    def __repr__(self):
        return "<Food {} of List {}>".format(
            self.name, self.list_.name
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'categories': [i.category.id for i in self.categories]
        }


class Meal(db.Model):
    """
    This is a meal, there will be one entry per meal per day

    Takes list_id, name and order
    """
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('list_id', 'name'),)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete="CASCADE"), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('meals', passive_deletes=True))

    # backref entries -> Entry

    def __repr__(self):
        return "<Meal {} of List {}>".format(
            self.name, self.list_.name
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Ingredient(db.Model):
    """
    Foods contain ingredients

    Takes food_id and name
    """
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    food_id = db.Column(db.Integer, db.ForeignKey(
        'foods.id', ondelete="CASCADE"))
    food = db.relationship("Food", backref=db.backref(
        'ingredients', passive_deletes=True))

    def __repr__(self):
        return "<Ingredient {} of Food {}>".format(
            self.name, self.food.name
        )


class ListSettings(db.Model):
    """
    Defines various settings for how a list is displayed, each user/list combo has one

    takes list_id, user_id, (start_day_of_week, days_to_display)
    """
    __tablename__ = 'listsettings'
    id = db.Column(db.Integer, primary_key=True)
    start_day_of_week = db.Column(db.Integer, default=-1)
    days_to_display = db.Column(db.Integer, default=7)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete='CASCADE'), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('settings', cascade="all", passive_deletes=True))

    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship(
        "User", backref=db.backref('listsettings', cascade="all", passive_deletes=True))

    def __repr__(self):
        return "<ListSettings {} of List {} for User {}>".format(
            self.id, self.list_.name, self.user.username
        )


class Day(db.Model):
    """
    A day is one day, has entries

    Takes list_id and day
    """
    __tablename__ = 'day'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False)

    __table_args__ = (db.UniqueConstraint('list_id', 'day'),)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete='CASCADE'), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('days', passive_deletes=True))

    def __repr__(self):
        return "<Day {} of List {}>".format(self.day, self.list_.name)

    def get_or_create_entries(self):
        meals = sorted(self.list_.get_or_create_meals(), key=lambda x: x.order)
        entries = []
        entry_names = [i for i in meals]
        for i in entry_names:
            entry = Entry.query.filter_by(
                day_id=self.id, meal_id=i.id).first()
            if not entry:
                entry = Entry(day_id=self.id, value='', meal_id=i.id)
                try:
                    db.session.add(entry)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    entry = Entry.query.filter_by(
                        day_id=self.id, meal_id=i.id).first()
            entries.append(entry)
        return entries

    def to_dict(self):
        return {
            'day': self.day.isoformat(),
            'id': self.id,
            'entries': [e.id for e in self.get_or_create_entries()]
        }


class Entry(db.Model):
    """
    One entry in the food planner

    Takes day_id, key (e.g lunch) and value (e.g. spaghetti)
    """
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(256), nullable=False, default='')

    __table_args__ = (db.UniqueConstraint('day_id', 'meal_id'),)

    day_id = db.Column(db.Integer, db.ForeignKey(
        'day.id', ondelete='CASCADE'), nullable=False)
    day = db.relationship('Day', backref=db.backref(
        'entries', passive_deletes=True))

    # TODO create this delete cascade relationship in many more places
    meal_id = db.Column(db.Integer, db.ForeignKey(
        'meals.id', ondelete='CASCADE'))
    meal = db.relationship(
        "Meal", backref=db.backref('entries', passive_deletes=True))

    def __repr__(self):
        return "<Entry {} of Day {} in List {}>".format(self.id, self.day.day, self.day.list_.name)

    def to_dict(self):
        return {
            'key': self.meal.name,
            'id': self.id,
            'value': self.value
        }


class ListPermission(db.Model):
    """
    Handles permissions for a user to a list

    Takes in user_id, list_id and permission_level (using owner or member)
    """
    __tablename__ = 'listpermission'
    id = db.Column(db.Integer, primary_key=True)
    permission_level = db.Column(db.String(256), nullable=False)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.id', ondelete='CASCADE'), nullable=False)
    list_ = db.relationship(
        "List", backref=db.backref('users', cascade="all", passive_deletes=True))

    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship(
        "User", backref=db.backref('lists', cascade="all", passive_deletes=True))

    def __repr__(self):
        return "<ListPermission {} of List {} to User {} at level {}>".format(
            self.id, self.list_.name, self.user.username, self.permission_level
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.user.username,
            'permission_level': self.permission_level
        }
