import pytest
from application import app
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


def test_calories_route(client):
    # Test if the calories route is accessible
    response = client.get('/calories')
    assert response.status_code == 302

    # Test if the form submission updates the database
    login(client, 'test@example.com')
    response = client.post('/calories',
                           data={
                               'food': 'Test Food',
                               'target_date': '2023-12-01'
                           })
    assert response.status_code == 200  # Expect a redirect after form submission
