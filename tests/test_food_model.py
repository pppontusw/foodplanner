from app import db
from app.models import Food, FoodCategory, FoodCategoryAssociation
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class FoodModelCase(AppModelCase):

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
