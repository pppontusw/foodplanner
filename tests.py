from datetime import date, timedelta
import unittest
from app import create_app, db
from app.models import User, List, Share, Day, Entry
from config import Config

def push_dummy_user():
  user = User(email='doodle@doodlydoo.com', username='doodle', is_confirmed=False)
  user.set_password('Test1234')
  db.session.add(user)
  db.session.commit()
  return user

def push_dummy_admin():
  user = User(
      email='doodle-admin@doodlydoo.com',
      username='doodle-admin',
      is_confirmed=False,
      is_admin=True
  )
  user.set_password('Test1234')
  db.session.add(user)
  db.session.commit()
  return user


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

  def test_password_hashing(self):
    u = User(email='doodle', username='doodle', is_confirmed=False)
    u.set_password('Hollydooie')
    self.assertTrue(u.check_password('Hollydooie'))
    self.assertFalse(u.check_password('BABAKOOOKO'))

  def test_pw_reset_token(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    self.assertEqual(u.verify_reset_password_token(u.get_reset_password_token()), u)


  def test_get_lists(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    self.assertEqual(u.get_lists(), [])
    l = List(owner_id=u.id, name='l')
    c = List(owner_id=u.id, name='c')
    db.session.add_all([l, c])
    db.session.commit()
    self.assertEqual(u.get_lists(), [l, c])
    v = User(email='poodle', username='poodle', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    x = List(owner_id=v.id, name='x')
    db.session.add(x)
    db.session.commit()
    self.assertEqual(v.get_lists(), [x])
    s = Share(owner_id=v.id, grantee_id=u.id, list_id=x.id)
    db.session.add(s)
    db.session.commit()
    self.assertEqual(u.get_lists(), [l, c, x])


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

  def test_generate_api_key(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = List(owner_id=u.id, name='l')
    db.session.add(l)
    db.session.commit()
    self.assertEqual(l.generate_api_key(), l.apikey)

  def test_get_users_with_access(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = List(owner_id=u.id, name='l')
    c = List(owner_id=u.id, name='c')
    db.session.add_all([l, c])
    db.session.commit()
    self.assertEqual(l.get_users_with_access(), [u.id])
    v = User(email='poodle', username='poodle', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    x = List(owner_id=v.id, name='x')
    db.session.add(x)
    db.session.commit()
    self.assertEqual(x.get_users_with_access(), [v.id])
    s = Share(owner_id=v.id, grantee_id=u.id, list_id=x.id)
    db.session.add(s)
    db.session.commit()
    self.assertEqual(x.get_users_with_access(), [u.id, v.id])

  def test_get_days(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = List(owner_id=u.id, name='l')
    c = List(owner_id=u.id, name='c')
    db.session.add_all([l, c])
    db.session.commit()
    self.assertTrue(len(l.get_days()) == 7)
    now = date.today()
    days = []
    for i in range(0, 7):
      delta = timedelta(days=i)
      day = Day(list_id=c.id, day=now+delta)
      days.append(day)
      db.session.add(day)
    db.session.commit()
    self.assertEqual(c.get_days(), days)


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

  def test_get_entries(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = List(owner_id=u.id, name='l')
    c = List(owner_id=u.id, name='c')
    db.session.add_all([l, c])
    db.session.commit()
    day_1 = l.get_days()[0]
    self.assertTrue(len(day_1.get_entries()) == 2)
    l.entry_names = 'Lunch,Dinner,Flop'
    db.session.commit()
    self.assertTrue(len(day_1.get_entries()) == 3)
    day_2 = c.get_days()[0]
    entry_names = c.entry_names.split(',')
    entries = []
    for i in entry_names:
      entry = Entry(day_id=day_2.id, key=i, value='Bookoo')
      entries.append(entry)
      db.session.add(entry)
    db.session.commit()
    self.assertEqual(day_2.get_entries(), entries)


class ShareModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_get_list(self):
    u = User(email='doodle', username='doodle', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    v = User(email='doodle2', username='doodle2', is_confirmed=True)
    db.session.add(u)
    db.session.commit()
    l = List(owner_id=u.id, name='l')
    db.session.add(l)
    db.session.commit()
    s = Share(owner_id=u.id, grantee_id=v.id, list_id=l.id)
    db.session.add(s)
    db.session.commit()
    self.assertEqual(s.get_list(), l)


class MainViewCase(unittest.TestCase):
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
    return self.test_client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

  def logout(self):
    return self.test_client.get('/auth/logout', follow_redirects=True)

  def test_delete_list(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='TestyList')
    db.session.add(l)
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertEqual(rsp.status, '200 OK')
      self.assertTrue(
          'TestyList' in html)
      rsp = self.test_client.post('/delete_list/' + str(l.id), data=dict(
          yes='yes'
      ))
      self.assertEqual(rsp.status, '302 FOUND')
      rsp = self.test_client.get('/lists')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertFalse(
          'TestyList' in html)

  def test_lists(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='TestyList')
    db.session.add(l)
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertEqual(rsp.status, '200 OK')
      self.assertTrue(
          'TestyList' in html)

  def test_list_view(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='TestyList')
    db.session.add(l)
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/list/' + str(l.id))
      html = rsp.get_data(as_text=True)
      self.assertEqual(rsp.status, '200 OK')
      self.assertTrue(
          'TestyList' in html)
      self.assertTrue('Monday' in html)
      self.assertTrue('Wednesday' in html)
      self.assertTrue('Friday' in html)

  def test_new_list(self):
    u = push_dummy_user()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertEqual(rsp.status, '200 OK')
      self.assertFalse(
          'TestyList' in html)
      rsp = self.test_client.post('/new_list', data=dict(
          name='TestyList'
      ))
      self.assertEqual(rsp.status, '302 FOUND')
      rsp = self.test_client.get('/lists')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'TestyList' in html)

  def test_api_update(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='TestyList')
    db.session.add(l)
    db.session.commit()
    day_1 = l.get_days()[0]
    entry_1 = day_1.get_entries()[0]
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/list/' + str(l.id))
      html = rsp.get_data(as_text=True)
      self.assertTrue('Argogaa' not in html)
      rsp = self.test_client.post('/api/update/' + str(entry_1.id), data=dict(
          value='Argogaa'
      ))
      self.assertEqual(rsp.status, '200 OK')
      rsp = self.test_client.get('/list/' + str(l.id))
      html = rsp.get_data(as_text=True)
      self.assertTrue('Argogaa' in html)

  def test_shared_lists_access(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='Arbitration')
    c = List(owner_id=u.id, name='Cherrypie')
    db.session.add_all([l, c])
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertTrue('Arbitration' in html)
      self.assertTrue('Cherrypie' in html)
    v = User(email='poodle', username='poodle', is_confirmed=True)
    db.session.add(v)
    db.session.commit()
    x = List(owner_id=v.id, name='Xylophone')
    db.session.add(x)
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertTrue('Xylophone' not in html)
      rsp = self.test_client.get('/list/' + str(x.id))
      self.assertEqual(rsp.status, '302 FOUND')
    s = Share(owner_id=v.id, grantee_id=u.id, list_id=x.id)
    db.session.add(s)
    db.session.commit()
    with self.test_client:
      self.login(u.username)
      rsp = self.test_client.get('/lists')
      html = rsp.get_data(as_text=True)
      self.assertTrue('Xylophone' in html)
      self.assertTrue('Arbitration' in html)
      self.assertTrue('Cherrypie' in html)
      rsp = self.test_client.get('/list/' + str(x.id))
      self.assertEqual(rsp.status, '200 OK')


  def test_unauthenticated(self):
    u = push_dummy_user()
    l = List(owner_id=u.id, name='TestyList')
    db.session.add(l)
    db.session.commit()
    day_1 = l.get_days()[0]
    entry_1 = day_1.get_entries()[0]
    rsp = self.test_client.post('/api/update/' + str(entry_1.id), data=dict(
        value='Argogaa'
    ))
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/new_list')
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/lists')
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/settings/' + str(l.id))
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/list/' + str(l.id))
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/list_added/' + str(l.id))
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/get_api_key/' + str(l.id))
    self.assertEqual(rsp.status, '302 FOUND')
    rsp = self.test_client.get('/delete_list/' + str(l.id))
    self.assertEqual(rsp.status, '302 FOUND')

class AdminViewCase(unittest.TestCase):
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
    return self.test_client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

  def logout(self):
    return self.test_client.get('/auth/logout', follow_redirects=True)

  def test_unauthenticated_admin_view(self):
    rsp = self.test_client.get('/admin/index')
    self.assertEqual(rsp.status, '302 FOUND')

  def test_regular_user_admin_view(self):
    user = push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.get('/admin/index')
      self.assertEqual(rsp.status, '302 FOUND')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'You should be redirected automatically to target URL: <a href="/">' in html)

  def test_admin_access_admin_view(self):
    user = push_dummy_admin()
    push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.get('/admin/index')
      html = rsp.get_data(as_text=True)
      self.assertEqual(rsp.status, '200 OK')
      self.assertTrue(
          'doodle-admin@doodlydoo.com' in html)
      self.assertTrue(
          'doodle@doodlydoo.com' in html)

  def test_admin_confirm_delete_user(self):
    user = push_dummy_admin()
    push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.get('/admin/deluser/2')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          '<p>You are about to permanently delete the user doodle@doodlydoo.com!</p><br>' in html)
      self.assertTrue(
          'Confirm' in html)
      self.assertTrue(
          'I regret my decision' in html)

  def test_admin_delete_user(self):
    user = push_dummy_admin()
    push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.post('/admin/deluser/2', data=dict(
          yes='yes'
      ))
      self.assertEqual(rsp.status, '302 FOUND')
      rsp = self.test_client.get('/admin/index')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'doodle-admin@doodlydoo.com' in html)
      self.assertFalse(
          'doodle@doodlydoo.com' in html)



class AuthViewCase(unittest.TestCase):
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

  def login(self, username, password='Test1234', follow_redirects=True):
    return self.test_client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=follow_redirects)

  def logout(self):
    return self.test_client.get('/auth/logout', follow_redirects=True)

  def test_login_view(self):
    rsp = self.test_client.get('/auth/login')
    self.assertEqual(rsp.status, '200 OK')
    html = rsp.get_data(as_text=True)
    self.assertTrue(
        '<input class="form-control" id="username" name="username" required type="text"'
        in html)
    self.assertTrue(
        '<input class="form-control" id="password" name="password" required type="password"'
        in html)

  def test_login(self):
    user = push_dummy_user()
    with self.test_client:
      rsp = self.login(user.username, 'kabonkadonk')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'Invalid username or password' in html)
      self.assertTrue(
          '<li><a href="/auth/login">Login</a></li>' in html)
      rsp = self.login(user.username)
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          '<li><a href="/auth/logout">Logout</a></li>' in html)

  def test_register_view(self):
    rsp = self.test_client.get('/auth/register')
    self.assertEqual(rsp.status, '200 OK')
    html = rsp.get_data(as_text=True)
    self.assertTrue(
        '<input class="form-control" id="email" name="email" required type="text" value="">'
        in html)
    self.assertTrue(
        '<input class="form-control" id="password" name="password" required type="password"'
        in html)

  def test_register(self):
    with self.test_client:
      email = 'boogieboo@boo.com'
      password = 'Test1234'
      rsp = self.test_client.post('/auth/register', data=dict(
          email=email,
          username=email,
          firstname='boo',
          lastname='boo',
          password=password,
          password2=password
      ))
      self.assertEqual(rsp.status, '302 FOUND')
    with self.test_client:
      self.login(email)
      rsp = self.test_client.get('/auth/user')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          '<input class="form-control" id="email" name="email" required type="text" value="'
          + email + '">' in html)
      self.assertTrue(
          '<input class="form-control" id="password" name="password" type="password" value="">'
          in html)

  def test_reset_password(self):
    user = push_dummy_user()
    rsp = self.test_client.post('/auth/reset_password_request', data=dict(
        email=user.email
    ))
    self.assertEqual(rsp.status, '302 FOUND')

  def test_profile_view(self):
    user = push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.get('/auth/user')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          '<input class="form-control" id="email" name="email" required type="text" value="'
          + user.email + '">' in html)
      self.assertTrue(
          '<input class="form-control" id="password" name="password" type="password" value="">'
          in html)

  def test_confirm_delete_self(self):
    user = push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.get('/auth/delete')
      self.assertEqual(rsp.status, '200 OK')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'Confirm' in html)
      self.assertTrue(
          'I regret my decision' in html)

  def test_delete_self(self):
    user = push_dummy_user()
    with self.test_client:
      self.login(user.username)
      rsp = self.test_client.post('/auth/delete', data=dict(
          yes='yes'
      ))
      self.assertEqual(rsp.status, '302 FOUND')
      rsp = self.test_client.get('/auth/user')
      self.assertEqual(rsp.status, '302 FOUND')
      html = rsp.get_data(as_text=True)
      self.assertTrue(
          'You should be redirected automatically to target URL:' in html)



if __name__ == '__main__':
  unittest.main(verbosity=1)
