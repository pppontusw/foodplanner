import unittest
from app import create_app, db
from app.models import Food, FoodCategory, FoodCategoryAssociation
from helpers import push_dummy_user, push_dummy_list, TestConfig


class FoodModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_food_repr(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = Food(list_id=list_.id, name='Food')
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.__repr__(), '<Food Food of List List>')

    def test_food_to_dict(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = Food(list_id=list_.id, name='Food')
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.to_dict(), {
            'id': 1,
            'name': 'Food',
            'categories': []
        })
        cat = FoodCategory(list_id=list_.id, name='Cat')
        db.session.add(cat)
        db.session.commit()
        catass = FoodCategoryAssociation(food_id=a.id, category_id=cat.id)
        db.session.add(catass)
        db.session.commit()
        self.assertEqual(a.to_dict(), {
            'id': 1,
            'name': 'Food',
            'categories': [1]
        })
