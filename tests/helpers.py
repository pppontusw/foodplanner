import unittest
from app import db, create_app
from app.models import User, List, ListPermission
from config import Config


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password='Test1234'):
        return self.test_client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })

    def logout(self):
        return self.test_client.get('/api/auth/logout', follow_redirects=True)


class AppModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


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
