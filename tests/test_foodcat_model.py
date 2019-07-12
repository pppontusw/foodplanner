from app import db
from app.models import FoodCategory
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class FoodCategoryModelCase(AppModelCase):
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
