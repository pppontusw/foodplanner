import unittest
from app import create_app, db
from app.models import ListSettings
from helpers import push_dummy_user, push_dummy_list, TestConfig


class ListSettingsModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_repr_listsettings(self):
        a = push_dummy_user('a', 'a')
        list_ = push_dummy_list(a, 'list_')
        ls = ListSettings(list_id=list_.id, user_id=a.id)
        db.session.add(ls)
        db.session.commit()
        self.assertEqual(
            ls.__repr__(), '<ListSettings 1 of List list_ for User a>'
        )
