from app import db
from app.models import ListPermission, User
from helpers import (push_dummy_user,
                     push_dummy_list,
                     APITestCase)


class APIEntriesCase(APITestCase):

    def test_get_entries(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['key'], 'Lunch')
            self.assertEqual(
                data[0]['value'], '')

            rsp = self.test_client.get('/api/lists/1/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['key'], 'Lunch')
            self.assertEqual(
                data[0]['value'], '')

    def test_get_entries_nonexistant(self):
        u = push_dummy_user()
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/entries')
            self.assertEqual(rsp.status, '200 OK')

            rsp = self.test_client.get('/api/lists/1/entries')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            rsp = self.test_client.patch('/api/entries/1')
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_get_entries_offset(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/entries')

            # this is not the most useful test in the world
            # but it's better than nothing, I guess
            rsp = self.test_client.get('/api/entries?offset=1')
            data = rsp.get_json()
            self.assertEqual(
                data[0]['id'], 15)

            rsp = self.test_client.get('/api/lists/1/entries')

            # this is not the most useful test in the world
            # but it's better than nothing, I guess
            rsp = self.test_client.get('/api/lists/1/entries?offset=1')
            data = rsp.get_json()
            self.assertEqual(
                data[0]['id'], 15)

    def test_get_entries_limit(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/entries?limit=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(len(data) == 2)

            rsp = self.test_client.get('/api/entries?limit=30')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.get('/api/lists/1/entries?limit=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(len(data) == 2)

            rsp = self.test_client.get('/api/lists/1/entries?limit=30')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_entries_access_control(self):
        u = push_dummy_user()
        no_access_user = push_dummy_user(email='test', username='test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.logout()

        with self.test_client:
            no_access_user = User.query.filter_by(username='test').first()
            self.login(no_access_user.username)

            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [])

            rsp = self.test_client.get('/api/lists/1/entries')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            rsp = self.test_client.patch('/api/entries/1')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

    def test_entries_member_access(self):
        u = push_dummy_user()
        shared_to_user = push_dummy_user(email='test', username='test')
        list_ = push_dummy_list(u, 'TestyList')
        db.session.add(ListPermission(
            list_id=list_.id,
            user_id=shared_to_user.id,
            permission_level='member'))
        db.session.commit()
        with self.test_client:
            self.login(shared_to_user.username)

            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(
                len(data) == 14)

            rsp = self.test_client.patch('/api/entries/1', json=dict(
                value='Test'
            ))
            self.assertEqual(rsp.status, '200 OK')

    def test_entries_unauthenticated(self):
        u = push_dummy_user()
        push_dummy_list(u, 'Listy')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/entries')
            self.assertEqual(rsp.status, '200 OK')
            self.logout()
        rsp = self.test_client.get('/api/entries')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.get('/api/lists/1/entries')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.patch('/api/entries/1')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

    def test_patch_entries(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')

        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(
                len(data) == 14)

            rsp = self.test_client.patch('/api/entries/1', json=dict(
                value='Test'
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, {'key': 'Lunch', 'id': 1, 'value': 'Test'})

            rsp = self.test_client.get('/api/entries')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(data[0]['value'], 'Test')

            rsp = self.test_client.patch('/api/entries/1', data=dict(
                value='Test'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
