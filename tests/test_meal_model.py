from app import db
from app.models import Meal
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class MealModelCase(AppModelCase):

    def test_meal_repr(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = Meal(list_id=list_.id, name='Meal', order=0)
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.__repr__(), '<Meal Meal of List List>')

    def test_meal_to_dict(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        a = Meal(list_id=list_.id, name='Meal', order=0)
        db.session.add(a)
        db.session.commit()
        self.assertEqual(a.to_dict(), {
            'id': 1,
            'name': 'Meal'
        })
