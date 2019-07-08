from datetime import date
import unittest
from unittest.mock import patch
from app import create_app, db
from app.models import List, ListSettings, Meal
from helpers import push_dummy_user, push_dummy_list, TestConfig


class DayModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch.object(List, 'get_settings_for_user')
    def test_repr_day(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        a = push_dummy_user('a', 'a')
        list_ = push_dummy_list(a, 'list_')
        d = list_.get_or_create_days()[0]
        self.assertEqual(
            d.__repr__(), '<Day {} of List list_>'.format(d.day))

    @patch.object(List, 'get_settings_for_user')
    def test_get_or_create_entries(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'list_')
        day_1 = list_.get_or_create_days()[0]
        self.assertTrue(len(day_1.get_or_create_entries()) == 2)
        meal = Meal(name='test', list_id=list_.id, order=2)
        db.session.add(meal)
        db.session.commit()
        self.assertTrue(len(day_1.get_or_create_entries()) == 3)

    @patch.object(List, 'get_settings_for_user')
    def test_day_to_dict(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'list_')
        day_1 = list_.get_or_create_days()[0]
        self.assertEqual(day_1.to_dict(), {
            'day': date.today().isoformat(),
            'id': 1,
            'entries': [e.id for e in day_1.entries]
        })
