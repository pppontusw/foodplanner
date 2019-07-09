import unittest
from app import create_app, db
from app.models import User
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIUsersCase(unittest.TestCase):
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

    def test_get_users(self):
        user_1 = 'test1'
        user_2 = 'test2'
        u = User(email=user_1, firstname=user_1,
                 lastname=user_1, username=user_1)
        u.set_password('Test1234')
        db.session.add(u)
        db.session.commit()
        rsp = self.test_client.get('/api/users')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/users')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertEqual(data,
                             [
                                 {
                                     'email': 'test1',
                                     'firstname': 'test1',
                                     'id': 1,
                                     'lastname': 'test1',
                                     'username': 'test1'
                                 }
                             ])
            u2 = User(email=user_2, firstname=user_2,
                      lastname=user_2, username=user_2)
            db.session.add(u2)
            db.session.commit()
            rsp = self.test_client.get('/api/users')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertEqual(data,
                             [
                                 {
                                     'email': 'test1',
                                     'firstname': 'test1',
                                     'id': 1, 'lastname': 'test1',
                                     'username': 'test1'
                                 },
                                 {
                                     'id': 2,
                                     'username': 'test2'
                                 }
                             ])

    def test_post_users(self):
        rsp = self.test_client.post('/api/users')
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            email='Test',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')
        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')
        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test',
            firstname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test',
            firstname='Test',
            lastname='Test'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test',
            firstname='Test',
            lastname='Test',
            password='Test'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '201 CREATED')
        data = rsp.get_json()
        self.assertEqual(data['username'], 'Test')
        self.assertEqual(data['email'], 'Test')
        self.assertEqual(data['firstname'], 'Test')
        self.assertEqual(data['lastname'], 'Test')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test',
            email='Test2',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        rsp = self.test_client.post('/api/users', json=dict(
            username='Test2',
            email='Test',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '400 BAD REQUEST')

        with self.test_client:
            rsp = self.login('Test')
            self.assertEqual(rsp.status, '200 OK')

    def test_put_users(self):
        push_dummy_user()
        push_dummy_user('already_taken', 'already_taken')

        rsp = self.test_client.put('/api/users/1', json=dict(
            username='Test',
            email='Test',
            firstname='Test',
            lastname='Test',
            password='Test1234'
        ))
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

        with self.test_client:
            self.login('doodle')

            rsp = self.test_client.put('/api/users/1', json=dict(
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/users/1')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                firstname='Test',
                lastname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='Test',
                lastname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # you can actually put without password, this isn't maybe
            # 100% great design, but it fits, for now..
            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                lastname='Test'
            ))
            self.assertEqual(rsp.status, '200 OK')

            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # put to other user
            rsp = self.test_client.put('/api/users/2', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test'
            ))
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            # doesn't exist
            rsp = self.test_client.put('/api/users/50', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test'
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')

            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test12345'
            ))
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertEqual(data['username'], 'Test')
            self.assertEqual(data['email'], 'Test')
            self.assertEqual(data['firstname'], 'Test')
            self.assertEqual(data['lastname'], 'Test')

            rsp = self.test_client.put('/api/users/1', json=dict(
                username='Test',
                email='already_taken',
                firstname='Test',
                lastname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/users/1', json=dict(
                username='already_taken',
                email='Test',
                firstname='Test',
                lastname='Test',
                password='Test1234'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

        with self.test_client:
            rsp = self.login('Test', 'Test12345')
            self.assertEqual(rsp.status, '200 OK')

    def test_delete_users(self):
        u = push_dummy_user('user1', 'user1')
        push_dummy_user('user2', 'user2')

        # can't delete user when not authenticated
        rsp = self.test_client.delete('/api/users/1')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')

        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            # can't delete user that does not exist
            rsp = self.test_client.delete('/api/users/10')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            # can't delete another user
            rsp = self.test_client.delete('/api/users/2')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

            # can delete self
            rsp = self.test_client.delete('/api/users/1')
            self.assertEqual(rsp.status, '401 UNAUTHORIZED')
            data = rsp.get_json()
            self.assertEqual(data['msg'], 'User deleted')

        with self.test_client:
            self.login('user2')

            rsp = self.test_client.get('/api/users')
            data = rsp.get_json()
            self.assertFalse('user1' in [i['username'] for i in data])
            self.assertTrue('user2' in [i['username'] for i in data])
