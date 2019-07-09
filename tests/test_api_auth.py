import unittest
from app import create_app, db
from helpers import push_dummy_user, TestConfig


class APIAuthCase(unittest.TestCase):
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

    def test_login(self):
        push_dummy_user()

        rsp = self.test_client.post('/api/auth/login', json={
            'username': '5',
            'password': 'Test0000'
        })
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

        rsp = self.test_client.post('/api/auth/login', json={
            'username': 'doodle',
            'password': 'Test0000'
        })
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

        rsp = self.test_client.post('/api/auth/login', json={
            'password': 'Test0000'
        })
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/auth/login', json={
            'username': 'doodle'
        })
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/auth/login')
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        with self.test_client:
            rsp = self.login('doodle')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertEqual(data,
                             {
                                 'msg': 'Logged in successfully',
                                 'email': 'doodle@doodlydoo.com',
                                 'firstname': None,
                                 'id': 1,
                                 'lastname': None,
                                 'username': 'doodle'
                             }
                             )

    def test_auth_login_logout(self):

        push_dummy_user()

        rsp = self.test_client.get('/api/auth/user')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

        with self.test_client:
            rsp = self.login('doodle')
            self.assertEqual(rsp.status, '200 OK')

            rsp = self.test_client.get('/api/auth/user')
            self.assertEqual(rsp.status, '200 OK')

            data = rsp.get_json()
            self.assertEqual(data,
                             {
                                 'msg': 'Session still valid',
                                 'email': 'doodle@doodlydoo.com',
                                 'firstname': None,
                                 'id': 1,
                                 'lastname': None,
                                 'username': 'doodle'
                             }
                             )
            self.logout()

            rsp = self.test_client.get('/api/auth/user')
            self.assertEqual(rsp.status, '401 UNAUTHORIZED')
