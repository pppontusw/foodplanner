import unittest
from app import create_app, db
from app.models import FoodCategory
from helpers import push_dummy_user, push_dummy_list, TestConfig


class FoodCategoryModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_foodcat_repr(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = FoodCategory(list_id=list_.id, name='Category')
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.__repr__(), '<FoodCategory Category of List List>')

    def test_foodcat_to_dict(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = FoodCategory(list_id=list_.id, name='Category')
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.to_dict(), {
            'id': 1,
            'name': 'Category'
        })
