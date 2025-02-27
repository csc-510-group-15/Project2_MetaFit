import pytest
from application import app, mongo
import sys
import os
import datetime

sys.path.append(os.path.abspath(os.path.join('..')))

TEST_EMAIL = "testemail@gmail.com"


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def login(client, email):
    with client.session_transaction() as sess:
        sess['email'] = email


def test_dashboard_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/dashboard')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="dashboard">' in response.data


def test_water_intake_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/water')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="water">' in response.data


def test_log_calories_route(client):
    # Ensure that the route returns a successful status code
    login(client, TEST_EMAIL)
    response = client.get('/calories')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="calories">' in response.data


def test_burn_calories_route(client):
    # Ensure that the route returns a successful status code
    login(client, TEST_EMAIL)
    response = client.get('/workout')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="workout">' in response.data


def test_meal_planning_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/meal_plan')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="meal_plan">' in response.data


def test_exercises_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/exercise')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="exercise">' in response.data


def test_courses_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/feed')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="feed">' in response.data


def test_user_profile_route(client):
    # Ensure that the route returns a successful status code
    login(client, TEST_EMAIL)
    response = client.get('/user_profile')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="user_profile">' in response.data


def test_daily_quests_route(client):
    # Ensure that the route returns a successful status code
    login(client, TEST_EMAIL)
    response = client.get('/daily_challenge')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="daily_challenge">' in response.data


def test_badges_route(client):
    # Ensure that the route returns a successful status code
    login(client, TEST_EMAIL)
    response = client.get('/badges')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="badges">' in response.data


def test_friends_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/friends')
    assert response.status_code == 200
    # Ensure that the route renders the correct template
    assert b'<head id="friends">' in response.data