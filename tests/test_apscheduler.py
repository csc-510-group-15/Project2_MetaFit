import pytest
from app import scheduler, send_weekly_email, mongo
from datetime import datetime
from flask_apscheduler import APScheduler
from unittest.mock import patch, MagicMock

@pytest.fixture
def app_with_scheduler():
    """Set up an app instance with the scheduler."""
    from app import app
    app.config['TESTING'] = True
    scheduler.start()
    yield app
    scheduler.shutdown()

def test_weekly_email_job_scheduled(app_with_scheduler):
    """Test if the weekly email job is scheduled."""
    job = scheduler.get_job("Weekly Email Job")
    assert job is not None, "Weekly Email Job should be scheduled."
    assert job.trigger.day_of_week == "mon"
    assert job.trigger.hour == 8
    assert job.trigger.minute == 0

@patch("app.send_weekly_email")
def test_scheduled_weekly_email_function(mock_send_email, app_with_scheduler, mocker):
    """Test the weekly email job functionality."""
    mocker.patch("app.mongo.db.user.find", return_value=[{"email": "testuser@example.com"}])

    # Run the scheduled job manually
    from app import scheduled_weekly_email
    scheduled_weekly_email()

    # Verify send_weekly_email is called with correct parameters
    mock_send_email.assert_called_once_with("testuser@example.com")

@patch("smtplib.SMTP_SSL")
def test_send_weekly_email_function(mock_smtp, app_with_scheduler):
    """Test that send_weekly_email function sends an email without errors."""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Call send_weekly_email function
    from app import send_weekly_email
    send_weekly_email("testuser@example.com")

    # Verify email server is connected and email sent
    mock_server.login.assert_called_once_with("bogusdummy123@gmail.com", "helloworld123!")
    mock_server.send_message.assert_called_once()
    print("Email sending tested successfully.")
