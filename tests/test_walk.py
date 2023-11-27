import sys, os

sys.path.append(os.path.abspath(os.path.join('..')))
from flask import session
from flask.testing import FlaskClient
from application import app, mongo, EnrollForm
import pytest


# Fixture for creating a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_walk_route_enroll(client: FlaskClient):
    # Simulate an active session
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    # Simulate a POST request to the walk route with valid form data
    response = client.post('/walk',
                           data={'email': 'test@example.com'},
                           follow_redirects=True)

    # Assert that the response status code is 200
    assert response.status_code == 200


def test_walk_route_no_session_redirect(client: FlaskClient):
    # Simulate no session

    # Simulate a GET request to the walk route without an active session
    response = client.get('/walk', follow_redirects=True)

    # Assert that the response status code is 302 (redirect)
    assert response.status_code == 200
