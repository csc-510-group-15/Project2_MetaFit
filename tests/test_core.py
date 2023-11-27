from flask import session, url_for
from flask.testing import FlaskClient
from application import app, mongo
from application import EnrollForm

import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
import pytest

# Fixture for creating a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_core_route_enroll(client: FlaskClient, mocker):
    # Mock form data and EnrollForm
    form_data = {'email': 'test@example.com'}
    mocker.patch('application.EnrollForm', return_value=EnrollForm(data=form_data))

    # Mock MongoDB user collection
    mocker.patch('pymongo.collection.Collection.insert_one')

    # Simulate an active session
    with app.test_request_context('/core'):
        session['email'] = 'test@example.com'

    # Make a POST request to the core route with valid credentials
    response = client.post('/core', data=form_data, follow_redirects=True)

    assert response.status_code == 200

def test_core_route_no_session_redirect(client: FlaskClient):
    # Simulate no session
    with app.test_request_context('/core'):
        session.clear()

    # Make a GET request to the core route without an active session
    response = client.get('/core', follow_redirects=True)

    assert response.status_code == 200  # Expect a redirect status code

def test_core_route_get_request(client: FlaskClient):
    # Simulate an active session
    with app.test_request_context('/core'):
        session['email'] = 'test@example.com'

    # Make a GET request to the core route
    response = client.get('/core', follow_redirects=True)

    assert response.status_code == 200
