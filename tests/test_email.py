import pytest
from unittest.mock import patch
from application import add_food_entry_email_notification
from application import add_burn_entry_email_notification, send_2fa_email, app
import sys
import os
import mock

sys.path.append(os.path.abspath(os.path.join('..')))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_smtp():
    with patch('application.smtplib.SMTP_SSL') as mock_smtp:
        yield mock_smtp


def test_add_food_entry_email_notification(mock_smtp):
    email = 'test@example.com'
    food = 'Test Food'
    date = '2023-01-01'

    add_food_entry_email_notification(email, food, date)

    mock_smtp.return_value.__enter__.return_value.login.assert_called_once()
    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()


def test_add_burn_entry_email_notification(mock_smtp):
    email = 'test@example.com'
    burn = '100'
    date = '2023-01-01'

    add_burn_entry_email_notification(email, burn, date)

    mock_smtp.return_value.__enter__.return_value.login.assert_called_once()
    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()


def test_send_2fa_email(mock_smtp):
    email = 'test@example.com'
    two_factor_secret = '123456'  # Replace with the actual secret

    # Call the function
    send_2fa_email(email, two_factor_secret)

    # Assertions
    mock_smtp.assert_called_once_with('smtp.gmail.com', 465, context=mock.ANY)
    mock_smtp.return_value.__enter__.return_value.login.assert_called_once_with(
    'burnoutapp123@gmail.com',
    'xszyjpklynmwqsgh'
    )
    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()


# def test_send_email_route(client: FlaskClient, mock_smtp):
#     # Simulate an active session
#     with client.session_transaction() as sess:
#         sess['email'] = 'test@example.com'

#     # Simulate the MongoDB find result
#     mongo_result = [
#         {'date': '2023-01-01',
#          'email': 'test@example.com', 'calories': 500, 'burnout': 'High'},
#         # Add more data as needed
#     ]
#     with patch('pymongo.collection.Collection.find') as mongo_find_mock:
#         mongo_find_mock.return_value = mongo_result

#         # Simulate a POST request to the send_email route
#         response = client.post('/send_email',
#           data={'share': 'friend1@example.com'})

#         # Assert that the response status code is 200
#         assert response.status_code == 200
