from helpers import APITestCase, push_dummy_user, push_dummy_list


class ErrorBPCase(APITestCase):

    def test_404(self):
        rsp = self.test_client.get('/api/nothing')
        self.assertEqual(rsp.status, '404 NOT FOUND')

    def test_405(self):
        rsp = self.test_client.delete('/api/lists')
        self.assertEqual(rsp.status, '405 METHOD NOT ALLOWED')

    def test_500(self):
        u = push_dummy_user()
        push_dummy_list(u, 'TestyList')
        with self.test_client:
            self.login(u.username)
            self.app.config['DEBUG'] = False
            self.app.config['TESTING'] = False
            self.app.config['TESTING_500'] = True
            rsp = self.test_client.get('/api/zerodivision')
            self.assertEqual(rsp.status, '500 INTERNAL SERVER ERROR')
            self.app.config['TESTING_500'] = False
            rsp = self.test_client.get('/api/zerodivision')
            self.assertEqual(rsp.status, '404 NOT FOUND')
