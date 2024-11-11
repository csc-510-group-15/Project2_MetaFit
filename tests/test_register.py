import pytest
from application import app
import sys
import os
from flask import session
import mongomock

sys.path.append(os.path.abspath(os.path.join('..')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with mongomock.patch():
        with app.test_client() as client:
            yield client

def test_get_user(client):
    db = mongomock.MongoClient().db
    db.items.insert_one(
        {
            "name": "OjasTest",
            "password": "hshaksjn",
            "weight": 90,
            "height": 180,
            "target_weight": 80,
            "start_date": "2023-10-15",
            "target_date": "2023-11-15"
        }
    )
    response = client.get("/register")
    assert response.status_code == 200

def test_insert_user(client):
    response = client.post(
        "/register",
        json={
            "name": "OjasTest",
            "password": "hshaksjn",
            "weight": "90",
            "height": "180",
            "target_weight": "80",
            "start_date": "2023-10-15",
            "target_date": "2023-11-15"
        }
    )
    assert response.status_code == 200

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_redirect_to_verify_2fa(test_client, mocker):
    # Mock the send_2fa_email function
    mocker.patch(
        'application.send_2fa_email'
    )

    response = test_client.post(
        '/register',
        data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'weight': '150',
            'height': '170',
            'target_weight': '140',
            'target_date': '2023-01-01'
        },
        follow_redirects=True
    )
    assert response.status_code == 200

def test_register_redirect_to_home_when_logged_in(test_client):
    with app.test_request_context('/register'):
        session['email'] = 'test@example.com'

    response = test_client.get('/register', follow_redirects=True)
    assert response.status_code == 200
