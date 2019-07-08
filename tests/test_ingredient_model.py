import unittest
from app import create_app, db
from app.models import Food, Ingredient
from helpers import push_dummy_user, push_dummy_list, TestConfig


class IngredientModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_ingredient_repr(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = Food(list_id=list_.id, name='Food')
        db.session.add(a)
        db.session.commit()
        ing = Ingredient(food_id=a.id, name='Ingredient')
        db.session.add(ing)
        db.session.commit()
        self.assertEqual(
            ing.__repr__(), '<Ingredient Ingredient of Food Food>')
