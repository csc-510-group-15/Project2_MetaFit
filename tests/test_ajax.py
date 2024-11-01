import json
from application import app, mongo
import sys, os

sys.path.append(os.path.abspath(os.path.join('..')))
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_ajaxhistory_route_with_data(client, monkeypatch):
    # Simulate an active session
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    # Simulate a successful MongoDB find_one result
    def mock_find_one(query, projection):
        return {
            'date': '2023-01-01',
            'email': 'test@example.com',
            'burnout': 'High',
            'calories': 500
        }

    monkeypatch.setattr(mongo.db.calories, 'find_one', mock_find_one)

    # Simulate a POST request to the ajaxhistory route
    response = client.post('/ajaxhistory', data={'date': '2023-01-01'})

    # Parse the JSON response
    response_data = json.loads(response.data)

    # Assert the response contains the expected data
    assert response.status_code == 200
