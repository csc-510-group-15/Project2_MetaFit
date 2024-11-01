import pytest
from unittest.mock import patch
import sys
import os
from application import app
import mongomock
from flask import session
from application import UserProfileForm  #Replace with the actual import path
sys.path.append(os.path.abspath(os.path.join('..')))

@pytest.fixture
def client():
    with mongomock.patch():
        with app.test_client() as client:
            yield client


def test_get_user_profile(client):
    db = mongomock.MongoClient().db

    db.items.insert_one(
        {
            "email": "ojaskulkarni100@gmail.com",
            "weight": 90,
            "height": 180,
            "target_weight": 80,
            "goal": "75"
        }, )
    response = client.get("/user_profile")
    assert response.status_code == 302


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_user_profile_route(client, mocker):
    # Simulate an active session
    with app.test_request_context('/user_profile'):
        session['email'] = 'test@example.com'

    # Mock the MongoDB query
    mocker.patch('pymongo.collection.Collection.find_one',
                 return_value={
                     'email': 'test@example.com',
                     'height': 170,
                     'weight': 70,
                     'goal': 'Lose weight',
                     'target_weight': 65
                 })

    response = client.get('/user_profile', follow_redirects=True)

    assert response.status_code == 200


def test_user_profile_redirect_to_login_when_not_logged_in(client):
    response = client.get('/user_profile', follow_redirects=True)

    assert response.status_code == 200  # Or the status code you expect for the login page
