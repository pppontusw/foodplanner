from app import db
from app.models import User, ListPermission
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class ListPermissionModelCase(AppModelCase):

    def test_repr_listpermission(self):
        a = push_dummy_user('a', 'a')
        b = push_dummy_user('b', 'b')
        list_ = push_dummy_list(a, 'list_')
        lpm = ListPermission(list_id=list_.id, user_id=b.id,
                             permission_level='member')
        db.session.add(lpm)
        db.session.commit()
        self.assertEqual(
            lpm.__repr__(), '<ListPermission 2 of List list_ to User b at level member>')

    def test_get_list_from_list_permission(self):
        u = push_dummy_user()
        v = User(email='doodle2', username='doodle2', is_confirmed=True)
        db.session.add(v)
        db.session.commit()
        list_ = push_dummy_list(u, 'list_')
        s = ListPermission(user_id=v.id, list_id=list_.id,
                           permission_level='member')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(s.list_, list_)

    def test_list_permission_to_dict(self):
        u = push_dummy_user()
        push_dummy_list(u, 'List')
        listperm = ListPermission.query.first()
        self.assertEqual(listperm.to_dict(), {
            'id': 1,
            'username': u.username,
            'permission_level': 'owner'
        })
