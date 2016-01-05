import json
import unittest

from flask import request

from app import db
from config_secret import *
from main import app
from models import Comment


class FlaskLoginMixin:
    app = app.test_client()

    LOGIN_URL = '/login/'
    LOGOUT_URL = '/logout/'

    def login(self, email, password):
        return self.app.post(self.LOGIN_URL, data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.app.get(self.LOGOUT_URL, follow_redirects=True)


class LoginAndLogoutTest(unittest.TestCase, FlaskLoginMixin):
    def test_login(self):
        response = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Success' in response.data.decode())
        self.logout()

    def test_failed_login(self):
        response = self.login('admin@gmail.com', 'WRONG_PASSWORD')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Invalid' in response.data.decode())
        self.logout()

    def test_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('logged out' in response.data.decode())


class AccessTest(unittest.TestCase, FlaskLoginMixin):
    def test_admin_can_get_to_admin_page(self):
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        response = self.app.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Hello' in response.data.decode())
        self.logout()

    def test_non_logged_in_user_can_get_to_admin_page(self):
        self.logout()
        response = self.app.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('redirected' in response.data.decode())

    def test_normal_user_cannot_get_to_admin_page(self):
        self.login(NORMAL_EMAIL, NORMAL_PASSWORD)
        response = self.app.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('redirected' in response.data.decode())
        self.logout()

    def test_logging_out_prevents_access_to_admin_page(self):
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.logout()
        response = self.app.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('redirected' in response.data.decode())


class APITest(unittest.TestCase, FlaskLoginMixin):
    def setUp(self):
        self.comment_data = {
            'name': 'some user',
            'email': 'user@example.com',
            'url': 'http://localhost',
            'ip_address': '127.0.0.1',
            'body': 'test comment',
            'entry_id': 1,
        }

    def tearDown(self):
        q = Comment.query.filter(Comment.email == 'user@example.com').first()
        if q.name == 'some user':
            db.session.delete(q)
            db.session.commit()
        else:
            print('did not find comment in db!!!')

    def test_adding_and_getting_comment(self):

        # ADDING COMMENT
        response = self.app.post(
            '/api/comment',
            data=json.dumps(self.comment_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue('body' in response.data.decode())
        self.assertEqual(
            json.loads(response.data.decode())['body'],
            self.comment_data['body']
        )

        # GETTING COMMENT
        get_comment_response = self.app.get('/api/comment')
        self.assertEqual(get_comment_response.status_code, 200)
        self.assertTrue(
            json.loads(response.data.decode()) in
            json.loads(get_comment_response.data.decode())['objects']
        )


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_homepage_works(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()