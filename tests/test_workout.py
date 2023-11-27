import pytest
from flask import Flask, session
from application import app, mongo, CalorieForm, WorkoutForm, getDate
import sys,os
sys.path.append(os.path.abspath(os.path.join('..')))
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def login(client, email):
    with client.session_transaction() as sess:
        sess['email'] = email
def test_workout_route(client):
    # Test if the workout route is accessible
    response = client.get('/workout')
    assert response.status_code == 302

    # Test if the form submission updates the database
    login(client, 'test@example.com')
    response = client.post('/workout', data={'burnout': '150', 'target_date': '2023-12-01'})
    assert response.status_code == 302  # Expect a redirect after form submission

    # Check if the database is updated
    entry = mongo.db.calories.find_one({'email': 'test@example.com', 'date': '2023-12-01'})
    assert entry is not None
    assert entry['calories'] < 0  # Adjust this based on the actual calories calculation