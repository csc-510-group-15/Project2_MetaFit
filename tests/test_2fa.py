# tests/test_2fa.py

import pytest
from flask import session
from application import app, mongo
from application import TwoFactorForm
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_verify_2fa_route(client):
    with client.session_transaction() as sess:
        sess['registration_data'] = {'email': 'test@example.com'}
        sess['two_factor_secret'] = '123456'

    response = client.post('/verify_2fa', data={'two_factor_code': '123456'}, follow_redirects=True)

    assert response.status_code == 200

def test_invalid_2fa_code_route(client):
    with client.session_transaction() as sess:
        sess['registration_data'] = {'email': 'test@example.com'}
        sess['two_factor_secret'] = '123456'

    response = client.post('/verify_2fa', data={'two_factor_code': '654321'}, follow_redirects=True)

    assert response.status_code == 200
