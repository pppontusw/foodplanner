import unittest
from unittest.mock import patch
from app import db
from app.models import (User, List,
                        ListPermission, Day,
                        Entry, ListSettings)
from helpers import (
    push_dummy_user,
    push_dummy_list,
    AppModelCase)


class UserModelCase(AppModelCase):

    def test_repr_user(self):
        a = push_dummy_user('a', 'a')
        self.assertEqual(
            a.__repr__(), '<User a>')

    # doesn't work with sqlite
    @unittest.skip
    def test_delete_user(self):
        a = push_dummy_user('a', 'a')
        b = push_dummy_user('b', 'b')
        list_ = push_dummy_list(a, 'list_')
        d = list_.get_or_create_days()
        e = Entry(day_id=d[0].id)
        ls = ListSettings(list_id=list_.id, user_id=a.id)
        s = ListPermission(list_id=list_.id, user_id=b.id)
        db.session.add_all([e, ls, s])
        db.session.commit()
        self.assertEqual(User.query.first(), a)
        self.assertEqual(List.query.first(), list_)
        self.assertEqual(Entry.query.first(), e)
        self.assertEqual(Day.query.first(), d[0])
        self.assertEqual(ListSettings.query.first(), ls)
        self.assertEqual(ListPermission.query.filter_by(
            user_id=b.id).first(), s)
        db.session.delete(a)
        db.session.commit()
        self.assertEqual(User.query.first(), b)
        self.assertEqual(List.query.first(), None)
        self.assertEqual(Entry.query.first(), None)
        self.assertEqual(Day.query.first(), None)
        self.assertEqual(ListSettings.query.first(), None)
        self.assertEqual(ListPermission.query.filter_by(
            user_id=a.id).first(), None)

    def test_set_and_check_password(self):
        u = User(email='doodle', username='doodle', is_confirmed=False)
        u.set_password('Hollydooie')
        self.assertTrue(u.check_password('Hollydooie'))
        self.assertFalse(u.check_password('BABAKOOOKO'))

    def test_reset_password_tokens(self):
        u = push_dummy_user()
        a = u.get_reset_password_token()
        self.assertEqual(u.verify_reset_password_token(a), u)
        a += 'boo'
        self.assertFalse(u.verify_reset_password_token(a))
        self.assertFalse(u.verify_reset_password_token(''))

    def test_get_lists(self):
        u = User(email='doodle', username='doodle', is_confirmed=True)
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.get_lists(), [])
        list_ = push_dummy_list(u, 'list_')
        c = push_dummy_list(u, 'c')
        self.assertEqual(u.get_lists(), [list_, c])
        v = User(email='poodle', username='poodle', is_confirmed=True)
        db.session.add(v)
        db.session.commit()
        x = push_dummy_list(v, 'x')
        self.assertEqual(v.get_lists(), [x])
        s = ListPermission(user_id=u.id, list_id=x.id,
                           permission_level='member')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(u.get_lists(), [list_, c, x])

    @patch('flask_login.utils._get_user')
    def test_to_dict(self, patched_current_user):
        u = push_dummy_user()
        data = u.to_dict()
        self.assertEqual(data, {'id': u.id, 'username': u.username})
        patched_current_user.return_value = u
        data = u.to_dict()
        self.assertEqual(
            data, {
                'id': u.id,
                'username': u.username,
                'email': 'doodle@doodlydoo.com',
                'firstname': None,
                'lastname': None
            }
        )
