import unittest
from app import create_app, db
from app.models import List, FoodCategory, Food, FoodCategoryAssociation
from helpers import (push_dummy_user,
                     push_dummy_list,
                     TestConfig)


class APIFoodCategoryCase(unittest.TestCase):
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

    def test_get_categories(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/lists/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            list_ = List.query.first()
            db.session.add(FoodCategory(list_id=list_.id, name='Test'))

            rsp = self.test_client.get('/api/lists/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Test'
            }])

    def test_post_categories(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/categories', json=dict(
                name="NewCat"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewCat'
            }])

            rsp = self.test_client.get('/api/lists/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewCat'
            }])

            # same category can't be created again
            rsp = self.test_client.post('/api/lists/1/categories', json=dict(
                name="NewCat"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # mssing Name parameter
            rsp = self.test_client.post('/api/lists/1/categories', json=dict(
                asdasd="NewCat"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # not json
            rsp = self.test_client.post('/api/lists/1/categories', data=dict(
                name="NewCat"
            ))
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_delete_categories(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.post('/api/lists/1/categories', json=dict(
                name="NewCat"
            ))
            data = rsp.get_json()
            self.assertEqual(rsp.status, '201 CREATED')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'NewCat'
            }])

            rsp = self.test_client.delete('/api/lists/1/categories/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            rsp = self.test_client.delete('/api/lists/1/categories/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_get_category_by_food(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/foods/1/categories')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            list_ = List.query.first()
            food = Food(list_id=list_.id, name='Food')
            db.session.add(food)
            db.session.commit()

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            foodcat = FoodCategory(list_id=list_.id, name='Cat')
            db.session.add(foodcat)
            db.session.commit()
            foodcatass = FoodCategoryAssociation(
                food_id=food.id, category_id=foodcat.id)
            db.session.add(foodcatass)
            db.session.commit()

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Cat'
            }])

    def test_delete_category_by_food(self):
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

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Cat'
            }])

            rsp = self.test_client.delete('/api/foods/1/categories/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            # re-delete same one
            rsp = self.test_client.delete('/api/foods/1/categories/1')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # try to delete an id that doesn't exist
            rsp = self.test_client.delete('/api/foods/1/categories/10')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            # non-existant-food
            rsp = self.test_client.delete('/api/foods/5/categories/1')
            self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_post_category_by_food(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get('/api/foods/1/categories')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            list_ = List.query.first()
            food = Food(list_id=list_.id, name='Food')
            db.session.add(food)
            db.session.commit()

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [])

            foodcat = FoodCategory(list_id=list_.id, name='Cat')
            db.session.add(foodcat)
            db.session.commit()

            rsp = self.test_client.post('/api/foods/1/categories/1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Cat'
            }])

            rsp = self.test_client.get('/api/foods/1/categories')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(data, [{
                'id': 1,
                'name': 'Cat'
            }])

            # re-post the same
            rsp = self.test_client.post('/api/foods/1/categories/1')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            # non-existant-category
            rsp = self.test_client.post('/api/foods/1/categories/10')
            self.assertEqual(rsp.status, '404 NOT FOUND')

            # non-existant-food
            rsp = self.test_client.post('/api/foods/5/categories/1')
            self.assertEqual(rsp.status, '404 NOT FOUND')
