from app import db
from app.models import Food, Ingredient
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class IngredientModelCase(AppModelCase):

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
