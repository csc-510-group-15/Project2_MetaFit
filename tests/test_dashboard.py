import pytest
from application import app
import sys
import os

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

# ------------------------------
# Tests for routes when user is logged in
# ------------------------------


def test_dashboard_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'<head id="dashboard">' in response.data


def test_log_calories_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/calories')
    assert response.status_code == 200
    assert b'<head id="calories">' in response.data


def test_burn_calories_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/workout')
    assert response.status_code == 200
    assert b'<head id="workout">' in response.data


def test_user_profile_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/user_profile')
    assert response.status_code == 200
    assert b'<head id="user_profile">' in response.data


def test_daily_quests_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/daily_challenge')
    assert response.status_code == 200
    assert b'<head id="daily_challenge">' in response.data


def test_badges_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/badges')
    assert response.status_code == 200
    assert b'<head id="badges">' in response.data


# Public routes should return 200 regardless of login
def test_water_intake_route(client):
    response = client.get('/water')
    assert response.status_code == 200
    assert b'<head id="water">' in response.data


def test_meal_planning_route(client):
    response = client.get('/meal_plan')
    assert response.status_code == 200
    assert b'<head id="meal_plan">' in response.data


def test_exercises_route(client):
    response = client.get('/exercise')
    assert response.status_code == 200
    assert b'<head id="exercise">' in response.data


def test_courses_route(client):
    response = client.get('/feed')
    assert response.status_code == 200
    assert b'<head id="feed">' in response.data


def test_friends_route(client):
    response = client.get('/friends')
    assert response.status_code == 200
    assert b'<head id="friends">' in response.data


# ------------------------------
# Tests for routes when user is NOT logged in
# ------------------------------

def test_dashboard_route_without_login(client):
    response = client.get('/dashboard')
    # /dashboard is protected so should redirect to login
    assert response.status_code == 302


def test_log_calories_route_without_login(client):
    response = client.get('/calories')
    # /calories is protected
    assert response.status_code == 302


def test_burn_calories_route_without_login(client):
    response = client.get('/workout')
    # /workout is protected
    assert response.status_code == 302


def test_user_profile_route_without_login(client):
    response = client.get('/user_profile')
    # /user_profile is protected
    assert response.status_code == 302


def test_daily_quests_route_without_login(client):
    response = client.get('/daily_challenge')
    # /daily_challenge is protected
    assert response.status_code == 302


def test_badges_route_without_login(client):
    response = client.get('/badges')
    # /badges is protected
    assert response.status_code == 302


# For public routes, not logging in should still return 200.
def test_water_intake_route_without_login(client):
    response = client.get('/water')
    assert response.status_code == 200


def test_meal_planning_route_without_login(client):
    response = client.get('/meal_plan')
    assert response.status_code == 200


def test_exercises_route_without_login(client):
    response = client.get('/exercise')
    assert response.status_code == 200


def test_courses_route_without_login(client):
    response = client.get('/feed')
    assert response.status_code == 200


def test_friends_route_without_login(client):
    response = client.get('/friends')
    assert response.status_code == 200
