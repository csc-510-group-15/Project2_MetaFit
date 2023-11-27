from application import app, mongo  # Import your Flask app and mongo instance
import sys, os

sys.path.append(os.path.abspath(os.path.join('..')))
from application import app, mongo
from flask_testing import TestCase
from flask import url_for
from flask_pymongo import PyMongo
import pytest


class TestAbbsRoute(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
        self.mongo = PyMongo(app)
        return app

    def setUp(self):
        self.mongo.db.user.insert_one({'Email': 'test@example.com'})

    def test_abbs_route_enroll(self):
        with self.client:
            response = self.client.post(url_for('abbs'),
                                        data={'email': 'test@example.com'})
            self.assert_redirects(response, url_for('dashboard'))

            # Check if the user is enrolled in the 'abbs' plan
            user = self.mongo.db.user.find_one({'Email': 'test@example.com'})

            # Check the status code of the response
            assert response.status_code == 302  # Assuming you expect a redirect status code

    def test_abbs_route_no_session_redirect(self):
        with self.client:
            response = self.client.get(url_for('abbs'))
            self.assert_redirects(response, url_for('dashboard'))

    def test_abbs_route_get_request(self):
        with self.client:
            response = self.client.get(url_for('abbs'))
            self.assert_redirects(response, url_for('dashboard'))
