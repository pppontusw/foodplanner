from datetime import date, timedelta
from app import db
from app.models import List, ListPermission, ListSettings
from helpers import (push_dummy_user,
                     push_dummy_list,
                     APITestCase)


class APIDaysCase(APITestCase):
    def test_get_days(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/days')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['day'], date.today().isoformat())

    def test_get_days_no_list(self):
        u = push_dummy_user()
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/days')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [])

    def test_get_days_offset(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)

            rsp = self.test_client.get(f'/api/days?offset=1')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            nextweek = date.today() + timedelta(days=7)
            self.assertEqual(
                data[0]['id'], 1)
            self.assertEqual(
                data[0]['day'], nextweek.isoformat())

            rsp = self.test_client.get(f'/api/days?offset=-1')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            lastweek = date.today() - timedelta(days=7)
            self.assertEqual(
                data[0]['id'], 8)
            self.assertEqual(
                data[0]['day'], lastweek.isoformat())

            rsp = self.test_client.get(f'/api/lists/1/days?offset=1')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            nextweek = date.today() + timedelta(days=7)
            self.assertEqual(
                data[0]['id'], 1)
            self.assertEqual(
                data[0]['day'], nextweek.strftime('%a, %d %b %Y 00:00:00 GMT'))

            rsp = self.test_client.get(f'/api/lists/1/days?offset=-1')
            self.assertEqual(rsp.status, '200 OK')
            data = rsp.get_json()
            lastweek = date.today() - timedelta(days=7)
            self.assertEqual(
                data[0]['id'], 8)
            self.assertEqual(
                data[0]['day'], lastweek.strftime('%a, %d %b %Y 00:00:00 GMT'))

            rsp = self.test_client.get(f'/api/lists/1/days?offset=-5001')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

            rsp = self.test_client.get(f'/api/lists/1/days?offset=5001')
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_get_days_limit(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            rsp = self.test_client.get('/api/days?limit=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [{'id': 1, 'day': date.today().isoformat(), 'entries': [1, 2]}])
            rsp = self.test_client.get('/api/days?limit=30')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '400 BAD REQUEST')
            rsp = self.test_client.get('/api/lists/1/days?limit=1')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [{
                    'id': 1,
                    'day': date.today().strftime('%a, %d %b %Y 00:00:00 GMT'),
                    'entries': [1, 2]
                }])
            rsp = self.test_client.get('/api/lists/1/days?limit=30')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '400 BAD REQUEST')

    def test_get_days_start_today(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            list_ = List.query.first()
            appropriate_start_day = 5 if not date.today().weekday() == 5 else 3
            db.session.add(ListSettings(list_id=list_.id,
                                        user_id=u.id,
                                        start_day_of_week=appropriate_start_day,
                                        days_to_display=10))
            db.session.commit()

            rsp = self.test_client.get('/api/days?limit=2')
            data = rsp.get_json()
            self.assertNotEqual(
                data[0]['day'], date.today().isoformat())

            rsp = self.test_client.get('/api/days?start_today=True&limit=2')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['day'], date.today().isoformat())

            rsp = self.test_client.get('/api/lists/1/days?limit=2')
            data = rsp.get_json()
            self.assertNotEqual(
                data[0]['day'], date.today().strftime('%a, %d %b %Y 00:00:00 GMT'))

            rsp = self.test_client.get(
                '/api/lists/1/days?start_today=True&limit=2')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['day'], date.today().strftime('%a, %d %b %Y 00:00:00 GMT'))

    def test_days_access_control(self):
        u = push_dummy_user()
        no_access_user = push_dummy_user(email='test', username='test')
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(no_access_user.username)

            rsp = self.test_client.get('/api/days')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data, [])

            rsp = self.test_client.get('/api/lists/1/days')
            self.assertEqual(rsp.status, '403 FORBIDDEN')

    def test_days_member_access(self):
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

            rsp = self.test_client.get('/api/days')
            data = rsp.get_json()
            self.assertEqual(rsp.status, '200 OK')
            self.assertEqual(
                data[0]['day'], date.today().isoformat())

    def test_days_unauthenticated(self):
        rsp = self.test_client.get('/api/days')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        rsp = self.test_client.get('/api/lists/1/days')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
        u = push_dummy_user()
        push_dummy_list(u, 'Listy')
        rsp = self.test_client.get('/api/lists/1/days')
        self.assertEqual(rsp.status, '401 UNAUTHORIZED')
