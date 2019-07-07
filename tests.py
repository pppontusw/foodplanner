from datetime import date, timedelta
import unittest
from unittest.mock import patch
from app import create_app, db
# from app.auth.token import generate_confirmation_token, confirm_token
from app.models import User, List, ListPermission, Day, Entry, ListSettings
from config import Config


def push_dummy_user(email='doodle@doodlydoo.com', username='doodle'):
  user = User(email=email, username=username, is_confirmed=False)
  user.set_password('Test1234')
  db.session.add(user)
  db.session.commit()
  return user


def push_dummy_admin(email='doodle-admin@doodlydoo.com', username='doodle-admin'):
  user = User(
      email=email,
      username=username,
      is_confirmed=False,
      is_admin=True
  )
  user.set_password('Test1234')
  db.session.add(user)
  db.session.commit()
  return user


def push_dummy_list(user, name, level="owner"):
  l = List(name=name)
  db.session.add(l)
  db.session.commit()
  perm = ListPermission(user_id=user.id, list_id=l.id, permission_level=level)
  db.session.add(perm)
  db.session.commit()
  return l


class TestConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite://'
  WTF_CSRF_ENABLED = False
  SECRET_KEY = 'very-secret'


class UserModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_repr_user(self):
    a = push_dummy_user('a', 'a')
    self.assertEqual(
        a.__repr__(), '<User a>')

  # doesn't work with sqlite
  @unittest.skip
  def test_delete_user(self):
    a = push_dummy_user('a', 'a')
    b = push_dummy_user('b', 'b')
    l = push_dummy_list(a, 'l')
    d = l.get_or_create_days()
    e = Entry(day_id=d[0].id)
    ls = ListSettings(list_id=l.id, user_id=a.id)
    s = ListPermission(list_id=l.id, user_id=b.id)
    db.session.add_all([e, ls, s])
    db.session.commit()
    self.assertEqual(User.query.first(), a)
    self.assertEqual(List.query.first(), l)
    self.assertEqual(Entry.query.first(), e)
    self.assertEqual(Day.query.first(), d[0])
    self.assertEqual(ListSettings.query.first(), ls)
    self.assertEqual(ListPermission.query.filter_by(user_id=b.id).first(), s)
    db.session.delete(a)
    db.session.commit()
    self.assertEqual(User.query.first(), b)
    self.assertEqual(List.query.first(), None)
    self.assertEqual(Entry.query.first(), None)
    self.assertEqual(Day.query.first(), None)
    self.assertEqual(ListSettings.query.first(), None)
    self.assertEqual(ListPermission.query.filter_by(
        user_id=a.id).first(), None)

  def test_password_hashing(self):
    u = User(email='doodle', username='doodle', is_confirmed=False)
    u.set_password('Hollydooie')
    self.assertTrue(u.check_password('Hollydooie'))
    self.assertFalse(u.check_password('BABAKOOOKO'))

  def test_pw_reset_token(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    self.assertEqual(u.verify_reset_password_token(
        u.get_reset_password_token()), u)

  def test_get_lists(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    self.assertEqual(u.get_lists(), [])
    l = push_dummy_list(u, 'l')
    c = push_dummy_list(u, 'c')
    self.assertEqual(u.get_lists(), [l, c])
    v = User(email='poodle', username='poodle', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    x = push_dummy_list(v, 'x')
    self.assertEqual(v.get_lists(), [x])
    s = ListPermission(user_id=u.id, list_id=x.id, permission_level='member')
    db.session.add(s)
    db.session.commit()
    self.assertEqual(u.get_lists(), [l, c, x])

  def test_auth_tokens(self):
    u = push_dummy_user()
    a = u.get_reset_password_token()
    self.assertEqual(u.verify_reset_password_token(a), u)
    a += 'boo'
    self.assertFalse(u.verify_reset_password_token(a))
    self.assertFalse(u.verify_reset_password_token(''))


class ListModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_repr_list(self):
    a = push_dummy_user('a', 'a')
    l = push_dummy_list(a, 'l')
    self.assertEqual(
        l.__repr__(), '<List {}>'.format(l.name)
    )

  # doesn't work with sqlite
  @unittest.skip
  def test_delete_list(self):
    a = push_dummy_user('a', 'a')
    b = push_dummy_user('b', 'b')
    l = push_dummy_list(a, 'l')
    d = l.get_or_create_days()
    e = Entry(day_id=d[0].id)
    ls = ListSettings(list_id=l.id, user_id=a.id)
    s = ListPermission(list_id=l.id, permission_level='member', user_id=b.id)
    db.session.add_all([e, ls, s])
    db.session.commit()
    self.assertEqual(List.query.first(), l)
    self.assertEqual(Entry.query.first(), e)
    self.assertEqual(Day.query.first(), d[0])
    self.assertEqual(ListSettings.query.first(), ls)
    self.assertEqual(ListPermission.query.filter_by(user_id=b.id).first(), s)
    l.delete_list()
    self.assertEqual(List.query.first(), None)
    self.assertEqual(Entry.query.first(), None)
    self.assertEqual(Day.query.first(), None)
    self.assertEqual(ListSettings.query.first(), None)
    self.assertEqual(ListPermission.query.first(), None)

  def test_list_get_settings_for_user(self):
    a = push_dummy_user('a', 'a')
    b = push_dummy_user('b', 'b')
    l = push_dummy_list(a, 'l')
    ls = ListSettings(list_id=l.id, user_id=a.id,
                      start_day_of_week=6, days_to_display=21)
    db.session.add(ls)
    db.session.commit()
    self.assertEqual(l.get_settings_for_user(a), ls)
    self.assertTrue(l.get_settings_for_user(b).start_day_of_week == -1)
    self.assertTrue(l.get_settings_for_user(b).days_to_display == 7)

  def test_generate_api_key(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = push_dummy_list(u, 'l')
    self.assertEqual(l.generate_api_key(), l.apikey)

  def test_get_users_with_access(self):
    u = push_dummy_user()
    l = push_dummy_list(u, 'l')
    self.assertEqual(l.get_users_with_access(), [u])
    v = User(email='poodle', username='poodle', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    x = push_dummy_list(v, 'x')
    self.assertEqual(x.get_users_with_access(), [v])
    s = ListPermission(user_id=u.id, list_id=x.id, permission_level='member')
    db.session.add(s)
    db.session.commit()
    self.assertEqual(x.get_users_with_access(), [v, u])

  @patch.object(List, 'get_settings_for_user', return_value=ListSettings(start_day_of_week=-1, days_to_display=7))
  def test_get_or_create_days(self, mock_get_sett):
    u = push_dummy_user()
    l = push_dummy_list(u, 'l')
    c = push_dummy_list(u, 'c')
    self.assertTrue(len(l.get_or_create_days()) == 7)
    now = date.today()
    days = []
    for i in range(0, 7):
      delta = timedelta(days=i)
      day = Day(list_id=c.id, day=now+delta)
      days.append(day)
      db.session.add(day)
    db.session.commit()
    c_days = c.get_or_create_days()
    self.assertEqual(c_days, days)


class DayModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  @patch.object(List, 'get_settings_for_user', return_value=ListSettings(start_day_of_week=-1, days_to_display=7))
  def test_repr_day(self, mock_get_sett):
    a = push_dummy_user('a', 'a')
    l = push_dummy_list(a, 'l')
    d = l.get_or_create_days()[0]
    self.assertEqual(
        d.__repr__(), '<Day {} of List l>'.format(d.day))

  @patch.object(List, 'get_settings_for_user', return_value=ListSettings(start_day_of_week=-1, days_to_display=7))
  def test_get_or_create_entries(self, mock_get_sett):
    u = push_dummy_user()
    l = push_dummy_list(u, 'l')
    c = push_dummy_list(u, 'c')
    day_1 = l.get_or_create_days()[0]
    self.assertTrue(len(day_1.get_or_create_entries()) == 2)
    l.entry_names = 'Lunch,Dinner,Flop'
    db.session.commit()
    self.assertTrue(len(day_1.get_or_create_entries()) == 3)
    day_2 = c.get_or_create_days()[0]
    entry_names = c.entry_names.split(',')
    entries = []
    for i in entry_names:
      entry = Entry(day_id=day_2.id, key=i, value='Bookoo')
      entries.append(entry)
      db.session.add(entry)
    db.session.commit()
    self.assertEqual(day_2.get_or_create_entries(), entries)


class EntryModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  @patch.object(List, 'get_settings_for_user', return_value=ListSettings(start_day_of_week=-1, days_to_display=7))
  def test_repr_entry(self, mock_get_sett):
    a = push_dummy_user('a', 'a')
    l = push_dummy_list(a, 'l')
    d = l.get_or_create_days()[0]
    e = Entry(day_id=d.id)
    db.session.add(e)
    db.session.commit()
    self.assertEqual(
        e.__repr__(), '<Entry 1 of Day {} in List l>'.format(d.day)
    )


class ListSettingsModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_repr_listsettings(self):
    a = push_dummy_user('a', 'a')
    l = push_dummy_list(a, 'l')
    ls = ListSettings(list_id=l.id, user_id=a.id)
    db.session.add(ls)
    db.session.commit()
    self.assertEqual(
        ls.__repr__(), '<ListSettings 1 of List l for User a>'
    )


class ListPermissionModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_repr_listpermission(self):
    a = push_dummy_user('a', 'a')
    b = push_dummy_user('b', 'b')
    l = push_dummy_list(a, 'l')
    lpm = ListPermission(list_id=l.id, user_id=b.id, permission_level='member')
    db.session.add(lpm)
    db.session.commit()
    self.assertEqual(
        lpm.__repr__(), '<ListPermission 2 of List l to User b at level member>')

  def test_get_list(self):
    u = push_dummy_user()
    v = User(email='doodle2', username='doodle2', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    l = push_dummy_list(u, 'l')
    s = ListPermission(user_id=v.id, list_id=l.id, permission_level='member')
    db.session.add(s)
    db.session.commit()
    self.assertEqual(s.list_, l)


# class MainViewCase(unittest.TestCase):
#   def setUp(self):
#     self.app = create_app(TestConfig)
#     self.app_context = self.app.app_context()
#     self.app_context.push()
#     self.test_client = self.app.test_client()
#     db.create_all()

#   def tearDown(self):
#     db.session.remove()
#     db.drop_all()
#     self.app_context.pop()

#   def login(self, username, password='Test1234'):
#     return self.test_client.post('/auth/login', data=dict(
#         username=username,
#         password=password
#     ), follow_redirects=True)

#   def logout(self):
#     return self.test_client.get('/auth/logout', follow_redirects=True)

#   def test_delete_list(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, 'TestyList')
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertTrue(
#           'TestyList' in html)
#       rsp = self.test_client.post('/delete_list/' + str(l.id), data=dict(
#           yes='yes'
#       ))
#       self.assertEqual(rsp.status, '302 FOUND')
#       rsp = self.test_client.get('/lists')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertFalse(
#           'TestyList' in html)

#   def test_lists(self):
#     u = push_dummy_user()
#     push_dummy_list(u, 'TestyList')
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertTrue(
#           'TestyList' in html)

#   def test_list_view(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, 'TestyList')
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/list/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertTrue('Monday' in html)
#       self.assertTrue('Wednesday' in html)
#       self.assertTrue('Friday' in html)

#   def test_new_list(self):
#     u = push_dummy_user()
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertFalse(
#           'TestyList' in html)
#       rsp = self.test_client.post('/new_list', data=dict(
#           name='TestyList'
#       ))
#       self.assertEqual(rsp.status, '302 FOUND')
#       rsp = self.test_client.get('/lists')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'TestyList' in html)

#   def test_api_update(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, 'TestyList')
#     day_1 = l.get_or_create_days()[0]
#     entry_1 = day_1.get_or_create_entries()[0]
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/list/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertTrue('Argogaa' not in html)
#       rsp = self.test_client.post('/api/update/' + str(entry_1.id), data=dict(
#           value='Argogaa'
#       ))
#       self.assertEqual(rsp.status, '200 OK')
#       rsp = self.test_client.get('/list/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue('Argogaa' in html)

#   def test_shared_lists_access(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, 'Arbitration')
#     c = push_dummy_list(u, name='Cherrypie')
#     db.session.add_all([l, c])
#     db.session.commit()
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue('Arbitration' in html)
#       self.assertTrue('Cherrypie' in html)
#     v = User(email='poodle', username='poodle', is_confirmed=True)
#     db.session.add(v)
#     db.session.commit()
#     x = push_dummy_list(v, 'Xylophone')
#     db.session.add(x)
#     db.session.commit()
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue('Xylophone' not in html)
#       rsp = self.test_client.get('/list/' + str(x.id))
#       self.assertEqual(rsp.status, '302 FOUND')
#     s = ListPermission(user_id=u.id, list_id=x.id, permission_level='member')
#     db.session.add(s)
#     db.session.commit()
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/lists')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue('Xylophone' in html)
#       self.assertTrue('Arbitration' in html)
#       self.assertTrue('Cherrypie' in html)
#       rsp = self.test_client.get('/list/' + str(x.id))
#       self.assertEqual(rsp.status, '200 OK')

#   def test_list_settings(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, 'TestyList')
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/list/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue('#entry_30' not in html)
#       tomorrow = date.today() + timedelta(days=1)
#       rsp = self.test_client.post('/list_settings/' + str(l.id), data=dict(
#           name="TestyList",
#           daysToDisplay="15",
#           startDayOfTheWeek=str(tomorrow.weekday())
#       ))
#       self.assertEqual(rsp.status, '200 OK')
#       rsp = self.test_client.get('/list/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(html.count(tomorrow.strftime('%A')), 9)
#       self.assertTrue('#entry_30' in html)

#   def test_list_shares(self):
#     u = push_dummy_user()
#     v = push_dummy_user(email='User2800@user.com', username='user2800')
#     l = push_dummy_list(u, 'TestyList')
#     with self.test_client:
#       self.login(u.username)
#       rsp = self.test_client.get('/list_shares/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(v.username not in html)
#       rsp = self.test_client.post('/list_shares/' + str(l.id), data=dict(
#           target=v.username
#       ))
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '302 FOUND')
#       rsp = self.test_client.get('/list_shares/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(v.username in html)
#       rsp = self.test_client.get('/list/' + str(l.id))
#       self.assertEqual(rsp.status, '200 OK')
#       rsp = self.test_client.get('/list_shares/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(v.username in html)
#     with self.test_client:
#       self.login(v.username)
#       rsp = self.test_client.post('/list_settings/' + str(l.id), data=dict(
#           name="TestyList",
#           daysToDisplay="15",
#           startDayOfTheWeek="2"))
#       rsp = self.test_client.get('/list/' + str(l.id))
#       self.assertEqual(rsp.status, '200 OK')
#       rsp = self.test_client.get('/list_shares/' + str(l.id))
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(u.username in html)

#   def test_unauthenticated(self):
#     u = push_dummy_user()
#     l = push_dummy_list(u, name='TestyList')
#     db.session.add(l)
#     db.session.commit()
#     day_1 = l.get_or_create_days()[0]
#     entry_1 = day_1.get_or_create_entries()[0]
#     rsp = self.test_client.post('/api/update/' + str(entry_1.id), data=dict(
#         value='Argogaa'
#     ))
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/new_list')
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/lists')
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/settings/' + str(l.id))
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/list/' + str(l.id))
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/get_api_key/' + str(l.id))
#     self.assertEqual(rsp.status, '302 FOUND')
#     rsp = self.test_client.get('/delete_list/' + str(l.id))
#     self.assertEqual(rsp.status, '302 FOUND')


# class AdminViewCase(unittest.TestCase):
#   def setUp(self):
#     self.app = create_app(TestConfig)
#     self.app_context = self.app.app_context()
#     self.app_context.push()
#     self.test_client = self.app.test_client()
#     db.create_all()

#   def tearDown(self):
#     db.session.remove()
#     db.drop_all()
#     self.app_context.pop()

#   def login(self, username, password='Test1234'):
#     return self.test_client.post('/auth/login', data=dict(
#         username=username,
#         password=password
#     ), follow_redirects=True)

#   def logout(self):
#     return self.test_client.get('/auth/logout', follow_redirects=True)

#   def test_unauthenticated_admin_view(self):
#     rsp = self.test_client.get('/admin/index')
#     self.assertEqual(rsp.status, '302 FOUND')

#   def test_regular_user_admin_view(self):
#     user = push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.get('/admin/index')
#       self.assertEqual(rsp.status, '302 FOUND')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'You should be redirected automatically to target URL: <a href="/">' in html)

#   def test_admin_access_admin_view(self):
#     user = push_dummy_admin()
#     push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.get('/admin/index')
#       html = rsp.get_data(as_text=True)
#       self.assertEqual(rsp.status, '200 OK')
#       self.assertTrue(
#           'doodle-admin@doodlydoo.com' in html)
#       self.assertTrue(
#           'doodle@doodlydoo.com' in html)

#   def test_admin_confirm_delete_user(self):
#     user = push_dummy_admin()
#     push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.get('/admin/deluser/2')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           '<p>You are about to permanently delete the user doodle@doodlydoo.com!</p><br>' in html)
#       self.assertTrue(
#           'Confirm' in html)
#       self.assertTrue(
#           'I regret my decision' in html)

#   def test_admin_delete_user(self):
#     user = push_dummy_admin()
#     push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.post('/admin/deluser/2', data=dict(
#           yes='yes'
#       ))
#       self.assertEqual(rsp.status, '302 FOUND')
#       rsp = self.test_client.get('/admin/index')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'doodle-admin@doodlydoo.com' in html)
#       self.assertFalse(
#           'doodle@doodlydoo.com' in html)


# class AuthViewCase(unittest.TestCase):
#   def setUp(self):
#     self.app = create_app(TestConfig)
#     self.app_context = self.app.app_context()
#     self.app_context.push()
#     self.test_client = self.app.test_client()
#     db.create_all()

#   def tearDown(self):
#     db.session.remove()
#     db.drop_all()
#     self.app_context.pop()

#   def login(self, username, password='Test1234', follow_redirects=True):
#     return self.test_client.post('/auth/login', data=dict(
#         username=username,
#         password=password
#     ), follow_redirects=follow_redirects)

#   def logout(self):
#     return self.test_client.get('/auth/logout', follow_redirects=True)

#   def test_login_view(self):
#     rsp = self.test_client.get('/auth/login')
#     self.assertEqual(rsp.status, '200 OK')
#     html = rsp.get_data(as_text=True)
#     self.assertTrue(
#         '<input class="form-control" id="username" name="username" required type="text"'
#         in html)
#     self.assertTrue(
#         '<input class="form-control" id="password" name="password" required type="password"'
#         in html)

#   def test_login(self):
#     user = push_dummy_user()
#     with self.test_client:
#       rsp = self.login(user.username, 'kabonkadonk')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'Invalid username or password' in html)
#       self.assertTrue(
#           '<li><a href="/auth/login">Login</a></li>' in html)
#       rsp = self.login(user.username)
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           '<li><a href="/auth/logout">Logout</a></li>' in html)

#   def test_register_view(self):
#     rsp = self.test_client.get('/auth/register')
#     self.assertEqual(rsp.status, '200 OK')
#     html = rsp.get_data(as_text=True)
#     self.assertTrue(
#         '<input class="form-control" id="email" name="email" required type="text" value="">'
#         in html)
#     self.assertTrue(
#         '<input class="form-control" id="password" name="password" required type="password"'
#         in html)

#   def test_register(self):
#     with self.test_client:
#       email = 'boogieboo@boo.com'
#       password = 'Test1234'
#       rsp = self.test_client.post('/auth/register', data=dict(
#           email=email,
#           username=email,
#           firstname='boo',
#           lastname='boo',
#           password=password,
#           password2=password
#       ))
#       self.assertEqual(rsp.status, '302 FOUND')
#     with self.test_client:
#       self.login(email)
#       rsp = self.test_client.get('/auth/user')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           '<input class="form-control" id="email" name="email" required type="text" value="'
#           + email + '">' in html)
#       self.assertTrue(
#           '<input class="form-control" id="password" name="password" type="password" value="">'
#           in html)

#   def test_reset_password(self):
#     user = push_dummy_user()
#     rsp = self.test_client.post('/auth/reset_password_request', data=dict(
#         email=user.email
#     ))
#     self.assertEqual(rsp.status, '302 FOUND')

#   def test_profile_view(self):
#     user = push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.get('/auth/user')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           '<input class="form-control" id="email" name="email" required type="text" value="'
#           + user.email + '">' in html)
#       self.assertTrue(
#           '<input class="form-control" id="password" name="password" type="password" value="">'
#           in html)

#   def test_confirm_delete_self(self):
#     user = push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.get('/auth/delete')
#       self.assertEqual(rsp.status, '200 OK')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'Confirm' in html)
#       self.assertTrue(
#           'I regret my decision' in html)

#   def test_delete_self(self):
#     user = push_dummy_user()
#     with self.test_client:
#       self.login(user.username)
#       rsp = self.test_client.post('/auth/delete', data=dict(
#           yes='yes'
#       ))
#       self.assertEqual(rsp.status, '302 FOUND')
#       rsp = self.test_client.get('/auth/user')
#       self.assertEqual(rsp.status, '302 FOUND')
#       html = rsp.get_data(as_text=True)
#       self.assertTrue(
#           'You should be redirected automatically to target URL:' in html)

#   # def test_auth_tokens(self):
#   #   a = generate_confirmation_token('test@test.com')
#   #   self.assertEqual(confirm_token(a), 'test@test.com')
#   #   a += 'boo'
#   #   self.assertFalse(confirm_token(a))
#   #   self.assertFalse(confirm_token(''))


if __name__ == '__main__':
  unittest.main(verbosity=1)
