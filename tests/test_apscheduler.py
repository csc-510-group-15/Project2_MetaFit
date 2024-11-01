import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from application import app, mongo, get_weekly_summary, send_weekly_email, scheduled_weekly_email, scheduler


class WeeklySummaryTestCase(unittest.TestCase):

    def setUp(self):
        # Set up test client and application context
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Use a test database
        app.config[
            'MONGO_URI'] = 'mongodb://localhost:27017/your_database_test'

        # Clear the test collections
        mongo.db.calories.delete_many({})
        mongo.db.users.delete_many({})
        mongo.db.user.delete_many(
            {})  # Assuming 'user' collection holds user data

        # Insert test user
        self.user_email = 'test_user@example.com'
        mongo.db.user.insert_one({
            'email': self.user_email,
            'completed_challenges': {}
        })

    def tearDown(self):
        # Clean up after each test
        mongo.db.calories.delete_many({})
        mongo.db.users.delete_many({})
        mongo.db.user.delete_many({})
        self.app_context.pop()

    def test_get_weekly_summary_no_data(self):
        # Test with no calories burned and no challenges completed
        summary = get_weekly_summary(self.user_email)
        self.assertIn('Total calories burned this week: 0', summary)
        self.assertIn('Challenges completed: 0', summary)

    def test_get_weekly_summary_with_data(self):
        # Insert calories burned in the last week
        today = datetime.now()
        one_week_ago = today - timedelta(days=7)
        mongo.db.calories.insert_many([
            {
                'email': self.user_email,
                'date': today - timedelta(days=1),
                'calories': 500
            },
            {
                'email': self.user_email,
                'date': today - timedelta(days=3),
                'calories': 300
            },
        ])

        # Insert completed challenges
        completed_challenges = {
            f"{(today - timedelta(days=1)).strftime('%Y-%m-%d')}_Challenge1":
            True,
            f"{(today - timedelta(days=2)).strftime('%Y-%m-%d')}_Challenge2":
            True,
        }
        mongo.db.users.insert_one({
            'email': self.user_email,
            'completed_challenges': completed_challenges
        })

        # Call the function
        summary = get_weekly_summary(self.user_email)

        # Check the content
        self.assertIn('Total calories burned this week: 800', summary)
        self.assertIn('Challenges completed: 2', summary)
        self.assertIn(
            'I’ve burned 800 calories and completed 2 challenges this week! #CalorieApp',
            summary)

    @patch('smtplib.SMTP_SSL')
    def test_send_weekly_email(self, mock_smtp):
        # Create a mock SMTP server instance
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance

        # Call the function
        send_weekly_email(self.user_email)

        # Verify that SMTP_SSL was called with correct parameters
        mock_smtp.assert_called_with(app.config['MAIL_SERVER'],
                                     app.config['MAIL_PORT'])

        # Verify that login was called
        mock_server_instance.login.assert_called_with(
            app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        # Verify that send_message was called
        self.assertTrue(mock_server_instance.send_message.called)

        # Retrieve the email message that was sent
        sent_message = mock_server_instance.send_message.call_args[0][0]
        self.assertEqual(sent_message['To'], self.user_email)
        self.assertEqual(sent_message['From'], app.config['MAIL_USERNAME'])
        self.assertEqual(sent_message['Subject'],
                         'Your Weekly Progress Summary')

    @patch('application.send_weekly_email')
    def test_scheduled_weekly_email(self, mock_send_weekly_email):
        # Clear the 'user' collection to ensure only test users are present
        mongo.db.user.delete_many({})

        # Insert test users
        test_users = [
            {
                'email': 'user1@example.com'
            },
            {
                'email': 'user2@example.com'
            },
            {
                'email': 'user3@example.com'
            },
        ]
        mongo.db.user.insert_many(test_users)

        # Call the scheduled function
        scheduled_weekly_email()

        # Verify that send_weekly_email was called for each user
        calls = [unittest.mock.call(user['email']) for user in test_users]
        mock_send_weekly_email.assert_has_calls(calls, any_order=True)
        self.assertEqual(mock_send_weekly_email.call_count, len(test_users))

    def test_scheduler_job_configuration(self):
        # Verify that the job is added to the scheduler
        jobs = scheduler.get_jobs()
        job_ids = [job.id for job in jobs]
        self.assertIn('Weekly Email Job', job_ids)

        # Retrieve the job
        job = scheduler.get_job('Weekly Email Job')

        # Map field names to their corresponding field objects
        field_names = job.trigger.FIELD_NAMES
        fields = dict(zip(field_names, job.trigger.fields))

        # For the day_of_week field
        day_of_week_expr = fields['day_of_week'].expressions[0]
        self.assertEqual(str(day_of_week_expr), 'mon')

        # For the hour field
        hour_expr = fields['hour'].expressions[0]
        self.assertEqual(str(hour_expr), '8')

        # For the minute field
        minute_expr = fields['minute'].expressions[0]
        self.assertEqual(str(minute_expr), '0')


if __name__ == '__main__':
    unittest.main()
