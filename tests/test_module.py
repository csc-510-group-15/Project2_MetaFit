import unittest
import sys
import os
from application import app

sys.path.append(os.path.abspath(os.path.join('..')))

TEST_EMAIL = "testemail@gmail.com"


class BasicTestCase(unittest.TestCase):

    def test_logout(self):
        pass

        self.app = app.test_client()
        ans = self.app.get('/logout')
        self.assertEqual(ans.status_code, 200)

    def test_home(self):
        self.app = app.test_client()
        ans = self.app.get('/home')
        self.assertEqual(ans.status_code, 302)

    def test_login(self):
        self.app = app.test_client()
        ans = self.app.get('/login')
        self.assertEqual(ans.status_code, 200)

    def test_register(self):
        self.app = app.test_client()
        ans = self.app.get('/register')
        self.assertEqual(ans.status_code, 200)

    def test_dashboard(self):
        self.app = app.test_client()
        with self.app.session_transaction() as sess:
            sess['email'] = TEST_EMAIL
        ans = self.app.get('/dashboard')
        self.assertEqual(ans.status_code, 200)

    def test_friends(self):
        self.app = app.test_client()
        ans = self.app.get('/friends')
        self.assertEqual(ans.status_code, 200)

    def test_calories(self):
        self.app = app.test_client()
        ans = self.app.get('/calories')
        self.assertEqual(ans.status_code, 302)

    pass


if __name__ == '__main__':
    unittest.main()
