from app import db
from app.models import ListSettings
from helpers import push_dummy_user, push_dummy_list, AppModelCase


class ListSettingsModelCase(AppModelCase):

    def test_repr_listsettings(self):
        a = push_dummy_user('a', 'a')
        list_ = push_dummy_list(a, 'list_')
        ls = ListSettings(list_id=list_.id, user_id=a.id)
        db.session.add(ls)
        db.session.commit()
        self.assertEqual(
            ls.__repr__(), '<ListSettings 1 of List list_ for User a>'
        )
