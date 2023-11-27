import pytest
from flask import Flask, session
from application import app, mongo, CalorieForm, WorkoutForm, getDate
import sys, os

sys.path.append(os.path.abspath(os.path.join('..')))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def login(client, email):
    with client.session_transaction() as sess:
        sess['email'] = email


def test_bronze_list_page(client):
    # Test if the bronze_list_page route is accessible
    response = client.get('/bronze_list')
    assert response.status_code == 200

    # Test if the form submission updates the bronze list
    response = client.post('/bronze_list', data={'target_date': '2023-12-01'})
    assert response.status_code == 200  # Or adjust based on your expected behavior
