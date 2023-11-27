import pytest
from unittest.mock import patch
from application import add_food_entry_email_notification, add_burn_entry_email_notification, send_2fa_email
import sys,os
sys.path.append(os.path.abspath(os.path.join('..')))
import mock
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
    mock_smtp.return_value.__enter__.return_value.login.assert_called_once_with('burnoutapp123@gmail.com', 'xszyjpklynmwqsgh')
    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()    
