import pytest
from flask import session
from application import app, mongo
import sys, os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def login(client, email):
    with client.session_transaction() as sess:
        sess['email'] = email
        
        
sys.path.append(os.path.abspath(os.path.join('..')))
def test_hrx_route(client):
    # Test if the hrx route is accessible
    response = client.get('/hrx')
    assert response.status_code == 302  # Expect a redirect since the user is not logged in

    # Test if the form submission updates the database
    login(client, 'test@example.com')
    response = client.post('/hrx', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'You have succesfully enrolled in our hrx plan!' in response.data

    # Check if the database is updated
    entry = mongo.db.user.find_one({'Email': 'test@example.com', 'Status': 'hrx'})
    assert entry is not None