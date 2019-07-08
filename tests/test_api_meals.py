import unittest
from app import create_app, db
from app.models import List, Meal
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIMealCase(unittest.TestCase):
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

    def test_get_meals(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists/1/meals')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {'id': 1, 'name': 'Lunch'},
                {'id': 2, 'name': 'Dinner'}])

            list_ = List.query.first()
            db.session.add(Meal(list_id=list_.id, name='Test', order=2))
            db.session.commit()

            rsp = self.test_client.get('/api/lists/1/meals')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [
                    {'id': 1, 'name': 'Lunch'},
                    {'id': 2, 'name': 'Dinner'},
                    {'id': 3, 'name': 'Test'}])

    def test_post_meals(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                name="MyMeal"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'MyMeal'
            }])

            rsp = self.test_client.get('/api/lists/1/meals')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'MyMeal'
            }])

            # same food can't be created again
            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                name="MyMeal"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # mssing Name parameter
            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                asdasd="NewerFood"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # not json
            rsp = self.test_client.post('/api/lists/1/meals', data=dict(
                name="NewerFood"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                name="AnotherMeal"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [
                {
                    'id': 1,
                    'name': 'MyMeal'
                },
                {
                    'id': 2,
                    'name': 'AnotherMeal'
                }])

    def test_patch_meals(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                name="MyMeal"
            ))
            self.assertEqual(rsp.status, '201 CREATED')

            rsp = self.test_client.patch('/api/lists/1/meals/1', json=dict(
                name="NEW_STUFF"
            ))
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NEW_STUFF'
            }])

            rsp = self.test_client.patch('/api/lists/1/meals/1', json=dict(
                no_name="NEW_STUFF"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.patch('/api/lists/1/meals/1', data=dict(
                name="NEW_STUFF"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.patch('/api/lists/1/meals/6', json=dict(
                name="NEW_STUFF"
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_delete_meals(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/meals', json=dict(
                name="NewMeal"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')

            rsp = self.test_client.delete('/api/lists/1/meals/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {'id': 1, 'name': 'Lunch'},
                {'id': 2, 'name': 'Dinner'}])

            rsp = self.test_client.delete('/api/lists/1/meals/100')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_put_meals(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            list_ = List.query.first()
            meal1 = Meal(list_id=list_.id, name='Meal1', order=0)
            db.session.add(meal1)
            db.session.commit()

            meal2 = Meal(list_id=list_.id, name='Meal2', order=1)
            db.session.add(meal2)
            db.session.commit()

            rsp = self.test_client.put('/api/lists/1/meals', json=[
                {'id': 1, 'name': 'Meal1'},
                {'id': 2, 'name': 'Meal2'},
                {'name': 'Meal3'}
            ])
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {'id': 1, 'name': 'Meal1'},
                {'id': 2, 'name': 'Meal2'},
                {'id': 3, 'name': 'Meal3'}
            ])

            rsp = self.test_client.put('/api/lists/1/meals', json=[
                {'id': 1, 'name': 'Meal1'},
                {'name': 'Meal3'}
            ])
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [
                {'id': 1, 'name': 'Meal1'},
                {'id': 2, 'name': 'Meal3'}
            ])

            rsp = self.test_client.put('/api/lists/1/meals', json=[
                {'id': 1, 'name': 'Meal1'},
                {'id': 4000, 'name': 'Meal3'}
            ])
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/meals', json=[
                {'id': 1, 'name': 'Meal1'},
                {'id': 2}
            ])
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/meals', json=[])
            data = rsp.get_json()
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/meals', json=dict(
                name='SomethingTotallyWrong'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')
