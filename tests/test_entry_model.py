from unittest.mock import patch
from app import db
from app.models import List, ListSettings, Entry
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class EntryModelCase(AppModelCase):
    @patch.object(List, 'get_settings_for_user')
    def test_repr_entry(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        a = push_dummy_user('a', 'a')
        list_ = push_dummy_list(a, 'list_')
        d = list_.get_or_create_days()[0]
        e = Entry(day_id=d.id)
        db.session.add(e)
        db.session.commit()
        self.assertEqual(
            e.__repr__(), '<Entry 1 of Day {} in List list_>'.format(d.day)
        )

    @patch.object(List, 'get_settings_for_user')
    def test_entry_to_dict(self, mock_get_settings):
        mock_get_settings.return_value = ListSettings(
            start_day_of_week=-1, days_to_display=7)
        u = push_dummy_user()
        list_ = push_dummy_list(u, 'List')
        day = list_.get_or_create_days()[0]
        entry = day.get_or_create_entries()[0]
        self.assertEqual(entry.to_dict(), {
            'key': 'Lunch',
            'id': 1,
            'value': ''
        })
