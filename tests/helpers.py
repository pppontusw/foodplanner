from datetime import date, timedelta
import unittest
from unittest.mock import patch
from app import create_app, db
from app.models import (User, List,
                        ListPermission, Day,
                        Entry, ListSettings, Meal,
                        FoodCategory, Food, Ingredient,
                        FoodCategoryAssociation)
from config import Config


def push_dummy_user(email='doodle@doodlydoo.com', username='doodle'):
    user = User(email=email, username=username, is_confirmed=False)
    user.set_password('Test1234')
    db.session.add(user)
    db.session.commit()
    return user


def push_dummy_admin(email='doodle-admin@doodlydoo.com', username='doodle-admin'):
    user = User(
        email=email,
        username=username,
        is_confirmed=False,
        is_admin=True
    )
    user.set_password('Test1234')
    db.session.add(user)
    db.session.commit()
    return user


def push_dummy_list(user, name, level="owner"):
    list_ = List(name=name)
    db.session.add(list_)
    db.session.commit()
    perm = ListPermission(user_id=user.id, list_id=list_.id,
                          permission_level=level)
    db.session.add(perm)
    db.session.commit()
    return list_


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'very-secret'
