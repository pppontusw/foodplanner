import unittest
from app import create_app, db
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIListSettingsCase(unittest.TestCase):
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

    def test_put_list_settings(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=5,
                start_day_of_week="Friday"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['settings']['days_to_display'], 5)
            self.assertEqual(
                data[0]['settings']['start_day_of_week'], 'Friday')

            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=20,
                start_day_of_week="Today"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['settings']['days_to_display'], 20)
            self.assertEqual(
                data[0]['settings']['start_day_of_week'], 'Today')

            # missing params
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                start_day_of_week="Friday"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # missing param
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=5
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # too high displaydays
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=28,
                start_day_of_week="Today"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # incorrect start day
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=21,
                start_day_of_week=-9
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # negative days
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=-5,
                start_day_of_week="Today"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # not json
            rsp = self.test_client.put('/api/lists/1/settings', data=dict(
                days_to_display=-5,
                start_day_of_week="Today"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_put_list_settings_anonymous(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        rsp = self.test_client.put('/api/lists/1/settings', json=dict(
            days_to_display=5,
            start_day_of_week="Friday"
        ))
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

    def test_put_list_settings_nonexistant_list(self):
        u = push_dummy_user()
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.put('/api/lists/2/settings', json=dict(
                days_to_display=5,
                start_day_of_week="Friday"
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_put_list_settings_for_other_users_list(self):
        u = push_dummy_user()
        no_access_user = push_dummy_user(email='test', username='test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(no_access_user.username)
            rsp = self.test_client.put('/api/lists/1/settings', json=dict(
                days_to_display=5,
                start_day_of_week="Friday"
            ))
            self.assertEqual(rsp.status, '403 FORBIDDEN')
