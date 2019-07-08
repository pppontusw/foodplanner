from datetime import date, timedelta
import unittest
from app import create_app, db
from app.models import List, ListPermission
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIListsCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password='Test1234'):
        return self.test_client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })

    def logout(self):
        return self.test_client.get('/api/auth/logout', follow_redirects=True)

    def test_get_lists(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['name'], 'TestyList')
            self.assertTrue(
                data[0]['is_owner'])

    def test_get_lists_offset(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists?offset=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data[0]['days'], [1, 2, 3, 4, 5, 6, 7])
            list_ = List.query.first()
            rsp = self.test_client.get(f'/api/lists/{list_.id}/days?offset=1')
            data = rsp.get_json()
            nextweek = date.today() + timedelta(days=7)
            self.assertEqual(
                data[0]['id'], 1)
            self.assertEqual(
                data[0]['day'], nextweek.strftime('%a, %d %b %Y 00:00:00 GMT'))

    def test_get_lists_limit(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists?limit=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['days'], [1])
            rsp = self.test_client.get('/api/lists?limit=30')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_get_lists_start_today(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists?offset=-1&limit=2')
            data = rsp.get_json()
            rsp = self.test_client.get('/api/lists?start_today=True&limit=2')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['days'], [3, 4])
            list_ = List.query.first()
            rsp = self.test_client.get(f'/api/lists/{list_.id}/days')
            data = rsp.get_json()
            self.assertEqual(
                data[0]['id'], 3)
            self.assertEqual(
                data[0]['day'], date.today().strftime('%a, %d %b %Y 00:00:00 GMT'))

    def test_get_list(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['name'], 'TestyList')
            self.assertTrue(
                data[0]['is_owner'])

    def test_lists_cases_access_control(self):
        u = push_dummy_user()
        no_access_user = push_dummy_user(email='test', username='test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(no_access_user.username)

            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            rsp = self.test_client.get('/api/lists/1')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            rsp = self.test_client.delete('/api/lists/1')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            rsp = self.test_client.patch('/api/lists/1')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

    def test_lists_cases_member_access(self):
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

            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['name'], 'TestyList')

            rsp = self.test_client.get('/api/lists/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['name'], 'TestyList')
            self.assertFalse(
                data[0]['is_owner'])

            rsp = self.test_client.delete('/api/lists/1')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            rsp = self.test_client.patch('/api/lists/1', json=dict(
                listname='NewName'
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data[0]['name'], 'NewName')

    def test_lists_nonexistant(self):
        u = push_dummy_user()
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/lists/1')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            rsp = self.test_client.delete('/api/lists/1')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            rsp = self.test_client.patch('/api/lists/1', json=dict(
                listname='NewName'
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_lists_cases_unauthenticated(self):
        rsp = self.test_client.get('/api/lists')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.get('/api/lists/1')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.post('/api/lists', json=dict(
            listname='TestyList'
        ))
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        u = push_dummy_user()
        push_dummy_list(u, 'Listy')
        rsp = self.test_client.delete('/api/lists/1')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.patch('/api/lists/1')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

    def test_post_lists(self):
        u = push_dummy_user()
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [])
            # incorrect params
            rsp = self.test_client.post('/api/lists', json=dict(
                error='TestyList'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            # posting not json
            rsp = self.test_client.post('/api/lists', data=dict(
                error='TestyList'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            rsp = self.test_client.post('/api/lists', json=dict(
                listname='TestyList'
            ))
            self.assertEqual(rsp.status, '201 CREATED')
            rsp = self.test_client.post('/api/lists', json=dict(
                listname=''
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            rsp = self.test_client.get('/api/lists')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertTrue(
                data[0]['name'] == 'TestyList')
            self.assertTrue(
                data[0]['is_owner'])

    def test_delete_list(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertTrue(
                data[0]['name'] == 'TestyList')
            self.assertTrue(
                data[0]['is_owner'])
            list_ = List.query.first()
            rsp = self.test_client.delete('/api/lists/' + str(list_.id))
            self.assertEqual(rsp.status, '200 OK')
            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

    def test_patch_list(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.patch('/api/lists/1', json=dict(
                listname='NewName'
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data[0]['name'], 'NewName')

            # patching nonsense results in no changes
            rsp = self.test_client.patch('/api/lists/1', json=dict(
                hoopla='doopla'
            ))
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data[0]['name'], 'NewName')

            # verify
            rsp = self.test_client.get('/api/lists')
            data = rsp.get_json()
            self.assertEqual(data[0]['name'], 'NewName')

            # not json
            rsp = self.test_client.patch('/api/lists/1', data=dict(
                listname='NewName'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
