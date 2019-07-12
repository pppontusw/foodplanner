from datetime import date, timedelta
import unittest
from unittest.mock import patch
from app import create_app, db
from app.models import (List, ListPermission, ListSettings,
                        Entry, User, Day, Meal)
from helpers import push_dummy_user, push_dummy_list, TestConfig


class ListModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_repr_list(self):
        a = push_dummy_user('a', 'a')
        list_ = push_dummy_list(a, 'list_')
        self.assertEqual(
            list_.__repr__(), '<List {}>'.format(list_.name)
        )

    @unittest.skip  # NOT WORKING WITH SQLITE DB
    @patch.object(List, 'get_settings_for_user')
    def test_delete_list(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        a = push_dummy_user('a', 'a')
        b = push_dummy_user('b', 'b')
        list_ = push_dummy_list(a, 'list_')
        d = list_.get_or_create_days()
        e = Entry(day_id=d[0].id)
        ls = ListSettings(list_id=list_.id, user_id=a.id)
        s = ListPermission(
            list_id=list_.id, permission_level='member', user_id=b.id)
        db.session.add_all([e, ls, s])
        db.session.commit()
        self.assertEqual(List.query.first(), list_)
        self.assertEqual(Entry.query.first(), e)
        self.assertEqual(Day.query.first(), d[0])
        self.assertEqual(ListSettings.query.first(), ls)
        self.assertEqual(ListPermission.query.filter_by(
            user_id=b.id).first(), s)
        db.session.delete(list_)
        db.session.commit()
        self.assertEqual(List.query.first(), None)
        self.assertEqual(Entry.query.first(), None)
        self.assertEqual(Day.query.first(), None)
        self.assertEqual(ListSettings.query.first(), None)
        self.assertEqual(ListPermission.query.first(), None)

    def test_list_get_settings_for_user(self):
        a = push_dummy_user('a', 'a')
        b = push_dummy_user('b', 'b')
        list_ = push_dummy_list(a, 'list_')
        ls = ListSettings(list_id=list_.id, user_id=a.id,
                          start_day_of_week=6, days_to_display=21)
        db.session.add(ls)
        db.session.commit()
        self.assertEqual(list_.get_settings_for_user(a), ls)
        self.assertTrue(list_.get_settings_for_user(b).start_day_of_week == -1)
        self.assertTrue(list_.get_settings_for_user(b).days_to_display == 7)

    def test_generate_api_key(self):
        u = User(email='doodle', username='doodle', is_confirmed=True)
        db.session.add(u)
        db.session.commit()
        list_ = push_dummy_list(u, 'list_')
        self.assertEqual(list_.generate_api_key(), list_.apikey)

    def test_get_users_with_access(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'list_')
        self.assertEqual(list_.get_users_with_access(), [u])
        v = User(email='poodle', username='poodle', is_confirmed=True)
        db.session.add(v)
        db.session.commit()
        x = push_dummy_list(v, 'x')
        self.assertEqual(x.get_users_with_access(), [v])
        s = ListPermission(user_id=u.id, list_id=x.id,
                           permission_level='member')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(x.get_users_with_access(), [v, u])

    def test_get_owners_non_owners(self):
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'list_')
        v = User(email='poodle', username='poodle', is_confirmed=True)
        db.session.add(v)
        db.session.commit()
        s = ListPermission(user_id=v.id, list_id=list_.id,
                           permission_level='member')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(list_.get_owners(), [u])
        self.assertEqual(list_.get_non_owners(), [v])

    @patch.object(List, 'get_settings_for_user')
    def test_get_or_create_days(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'list_')
        c = push_dummy_list(u, 'c')
        self.assertTrue(len(list_.get_or_create_days()) == 7)
        now = date.today()
        days = []
        for i in range(0, 7):
            delta = timedelta(days=i)
            day = Day(list_id=c.id, day=now+delta)
            days.append(day)
            db.session.add(day)
        db.session.commit()
        c_days = c.get_or_create_days()
        self.assertEqual(c_days, days)

    def test_get_or_create_meals(self):
        u = push_dummy_user()
        list_no_meals = push_dummy_list(u, 'List')
        list_with_meals = push_dummy_list(u, 'List (With Meals)')
        list_no_meals.get_or_create_meals()
        self.assertEqual([{'id': i.id, 'name': i.name, 'order': i.order}
                          for i in list_no_meals.meals],
                         [{'id': 2, 'name': 'Dinner', 'order': 1},
                          {'id': 1, 'name': 'Lunch', 'order': 0}])
        new_meal = Meal(list_id=list_with_meals.id, name='Mymeal', order=0)
        db.session.add(new_meal)
        db.session.commit()
        list_with_meals.get_or_create_meals()
        self.assertEqual(
            [{'id': i.id, 'name': i.name, 'order': i.order}
             for i in list_with_meals.meals],
            [{'id': 3, 'name': 'Mymeal', 'order': 0}])

    def test_get_previous_of_weekday(self):
        today = date.today().weekday()
        for i in range(7):
            if today == i:
                res = 0
            elif i - today < 0:
                res = i - today
            else:
                res = i - today - 7
            self.assertEqual(List.get_previous_of_weekday(i), res)

    def test_get_weekday_from_int(self):
        self.assertEqual(List.get_weekday_from_int(-1), "Today")
        self.assertEqual(List.get_weekday_from_int(0), "Monday")
        self.assertEqual(List.get_weekday_from_int(1), "Tuesday")
        self.assertEqual(List.get_weekday_from_int(2), "Wednesday")
        self.assertEqual(List.get_weekday_from_int(3), "Thursday")
        self.assertEqual(List.get_weekday_from_int(4), "Friday")
        self.assertEqual(List.get_weekday_from_int(5), "Saturday")
        self.assertEqual(List.get_weekday_from_int(6), "Sunday")
        with self.assertRaises(ValueError):
            List.get_weekday_from_int(10)
        with self.assertRaises(ValueError):
            List.get_weekday_from_int(-2)

    @patch('flask_login.utils._get_user')
    def test_get_start_day(self, patched_current_user):
        u = push_dummy_user()
        patched_current_user.return_value = u
        list_with_minus_one = push_dummy_list(u, 'List')
        list_with_five = push_dummy_list(u, 'List')
        a = ListSettings(list_id=list_with_minus_one.id,
                         user_id=u.id, start_day_of_week=-1)
        b = ListSettings(list_id=list_with_five.id,
                         user_id=u.id, start_day_of_week=5)
        db.session.add_all([a, b])
        db.session.commit()
        c = 5 - date.today().weekday() if 5 - date.today().weekday() < 0 else 5 - \
            date.today().weekday() - 7
        self.assertEqual(list_with_minus_one.get_start_day(), 0)
        self.assertEqual(list_with_five.get_start_day(), c)

    @patch.object(List, 'get_settings_for_user')
    @patch('flask_login.utils._get_user')
    def test_list_to_dict(self, patched_current_user, mock_get_settings):
        u = push_dummy_user()
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        patched_current_user.return_value = u
        list_ = push_dummy_list(u, 'List')
        dict_ = list_.to_dict()
        self.assertEqual(dict_, {
            'name': 'List',
            'id': 1,
            'days': [
                1, 2, 3, 4, 5, 6, 7
            ],
            'settings': {
                'start_day_of_week': 'Today',
                'days_to_display': 7
            },
            'shares': [1],
            'is_owner': True,
            'meals': [1, 2],
            'foods': [],
            'categories': []
        })
