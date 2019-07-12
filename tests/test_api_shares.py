from app import db
from app.models import User, List, ListPermission
from helpers import (push_dummy_user,
                     push_dummy_list,
                     APITestCase)


class APISharesCase(APITestCase):

    def test_get_shares(self):
        u = push_dummy_user()
        v = push_dummy_user('test', 'test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists/1/shares')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {
                    'id': 1,
                    'username': 'doodle',
                    'permission_level': 'owner'
                }
            ])
            list_ = List.query.first()
            v = User.query.filter_by(username='test').first()
            db.session.add(ListPermission(
                list_id=list_.id,
                user_id=v.id,
                permission_level='member'))
            db.session.commit()
            rsp = self.test_client.get('/api/lists/1/shares')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {
                    'id': 1,
                    'username': 'doodle',
                    'permission_level': 'owner'
                },
                {
                    'id': 2,
                    'username': 'test',
                    'permission_level': 'member'
                }
            ])

    def test_post_shares(self):
        u = push_dummy_user()
        push_dummy_user('test', 'test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            v = User.query.filter_by(username='test').first()
            rsp = self.test_client.post('/api/lists/1/shares', json=dict(
                username=v.username
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [
                {
                    'id': 1,
                    'username': 'doodle',
                    'permission_level': 'owner'
                },
                {
                    'id': 2,
                    'username': 'test',
                    'permission_level': 'member'
                }
            ])

            # not json
            rsp = self.test_client.post('/api/lists/1/shares', data=dict(
                username=v.username
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # no username param
            rsp = self.test_client.post('/api/lists/1/shares', json=dict(
                avada=v.username
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # not a real username
            rsp = self.test_client.post('/api/lists/1/shares', json=dict(
                username='not_a_username!'
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')

            # user already has access
            rsp = self.test_client.post('/api/lists/1/shares', json=dict(
                username=v.username
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_delete_share(self):
        u = push_dummy_user()
        v = push_dummy_user('test', 'test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            # set up the new share
            list_ = List.query.first()
            v = User.query.filter_by(username='test').first()
            db.session.add(ListPermission(
                list_id=list_.id,
                user_id=v.id,
                permission_level='member'))
            db.session.commit()
            listperm = ListPermission.query.filter_by(user_id=v.id).first()

            # delete the share
            rsp = self.test_client.delete(
                '/api/lists/1/shares/' + str(listperm.id))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {
                    'id': 1,
                    'username': 'doodle',
                    'permission_level': 'owner'
                }
            ])

            # and now it's gone
            rsp = self.test_client.delete(
                '/api/lists/1/shares/' + str(listperm.id))
            self.assertEqual(rsp.status, '404 NOT FOUND')
