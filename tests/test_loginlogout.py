from flask import Flask, session
from flask.testing import FlaskClient
from flask import url_for
from application import app, mongo  # Replace 'your_flask_app_file' with the actual filename
from application import LoginForm  # Replace 'your_login_form_file' with the actual filename
import pytest
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
def test_login_route(client: FlaskClient):
    # Assuming you have a test user in your database
    test_user = {'email': 'test@example.com', 'password': 'hashed_password'}
    mongo.db.user.insert_one(test_user)

    # Make a POST request to the login route with valid credentials
    response = client.post(
        '/login',
        data={'email': 'test@example.com', 'password': 'password'},
        follow_redirects=True
    )

    assert response.status_code == 200


def test_logout_route(client: FlaskClient):
    # Simulate a logged-in user by setting a session variable
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    # Make a request to the logout route
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert session.get('email') is None
    # Add more assertions as needed

