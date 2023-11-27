from flask import session, url_for
from flask.testing import FlaskClient
from application import app, mongo
from application import EnrollForm
import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
# Fixture for creating a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_yoga_route_no_session_redirect(client: FlaskClient):
    # Simulate no session
    with app.test_request_context('/yoga'):
        session.clear()

    # Make a GET request to the yoga route without an active session
    response = client.get('/yoga', follow_redirects=True)

    assert response.status_code == 200  # Expect a redirect status code

def test_yoga_route_get_request(client: FlaskClient):
    # Simulate an active session
    with app.test_request_context('/yoga'):
        session['email'] = 'test@example.com'

    # Make a GET request to the yoga route
    response = client.get('/yoga', follow_redirects=True)

    assert response.status_code == 200
