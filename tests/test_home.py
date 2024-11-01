# tests/test_home.py

import pytest
from application import app
import sys
import os

sys.path.append(os.path.abspath(os.path.join('..')))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_redirect_to_login(client):
    response = client.get('/home', follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data
