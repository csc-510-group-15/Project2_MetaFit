import pytest
from flask import Flask, url_for, render_template
from application import app  # Replace 'your_flask_app_file' with the actual filename
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard_route(client):
    # Ensure that the route returns a successful status code
    response = client.get('/dashboard')
    assert response.status_code == 200

    # Ensure that the route renders the dashboard.html template
    assert b'Dashboard' in response.data  # Assuming 'Dashboard' is present in the rendered HTML