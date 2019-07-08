import unittest
from app import create_app, db
from app.models import List, FoodCategory, Food, FoodCategoryAssociation
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIFoodCase(unittest.TestCase):
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

    def test_get_foods(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists/1/foods')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            list_ = List.query.first()
            db.session.add(Food(list_id=list_.id, name='Test'))
            db.session.commit()

            rsp = self.test_client.get('/api/lists/1/foods')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Test',
                'categories': []
            }])

    def test_post_foods(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/foods', json=dict(
                name="NewFood"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewFood',
                'categories': []
            }])

            rsp = self.test_client.get('/api/lists/1/foods')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewFood',
                'categories': []
            }])

            # same food can't be created again
            rsp = self.test_client.post('/api/lists/1/foods', json=dict(
                name="NewFood"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # mssing Name parameter
            rsp = self.test_client.post('/api/lists/1/foods', json=dict(
                asdasd="NewerFood"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # not json
            rsp = self.test_client.post('/api/lists/1/foods', data=dict(
                name="NewerFood"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_delete_foods(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/foods', json=dict(
                name="NewFood"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewFood',
                'categories': []
            }])

            rsp = self.test_client.delete('/api/lists/1/foods/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            rsp = self.test_client.delete('/api/lists/1/foods/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_put_food(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            list_ = List.query.first()
            food = Food(list_id=list_.id, name='Food')
            db.session.add(food)
            db.session.commit()

            foodcat = FoodCategory(list_id=list_.id, name='Cat')
            db.session.add(foodcat)
            db.session.commit()
            foodcatass = FoodCategoryAssociation(
                food_id=food.id, category_id=foodcat.id)
            db.session.add(foodcatass)
            db.session.commit()

            foodcat = FoodCategory(list_id=list_.id, name='Cat_Remove')
            db.session.add(foodcat)
            db.session.commit()
            foodcatass = FoodCategoryAssociation(
                food_id=food.id, category_id=foodcat.id)
            db.session.add(foodcatass)
            db.session.commit()

            foodcat = FoodCategory(list_id=list_.id, name='Cat_Add')
            db.session.add(foodcat)
            db.session.commit()

            rsp = self.test_client.get('/api/lists/1/foods')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Food',
                'categories': [1, 2]
            }])

            rsp = self.test_client.put('/api/lists/1/foods/1', json=dict(
                name='UpdatedFood',
                categories=[
                    'Cat',
                    'NewCat',
                    'Cat_Add'
                ]
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'UpdatedFood',
                'categories': [1, 4, 3]
            }])

            rsp = self.test_client.put('/api/lists/1/foods/1', json=dict(
                name='UpdatedFood'
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/foods/1', json=dict(
                categories=['UpdatedFood']
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/foods/1', data=dict(
                name='UpdatedFood',
                categories=[
                    'Cat',
                    'NewCat'
                ]
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.put('/api/lists/1/foods/5', json=dict(
                name='UpdatedFood',
                categories=[
                    'Cat',
                    'NewCat'
                ]
            ))
            self.assertEqual(rsp.status, '404 NOT FOUND')
