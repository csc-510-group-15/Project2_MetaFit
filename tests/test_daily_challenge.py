import html
import unittest
from application import app, mongo
from datetime import datetime
import random


class DailyChallengeTestCase(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_test'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Clear the database collections
        mongo.db.users.delete_many({})

        # Insert a test user
        self.user_email = 'test_user@example.com'
        mongo.db.users.insert_one({
            'email': self.user_email,
            'completed_challenges': {}
        })

    def tearDown(self):
        # Clean up after each test
        mongo.db.users.delete_many({})
        self.app_context.pop()

    def test_daily_challenge_access(self):
        # Simulate a logged-in user
        with self.app.session_transaction() as sess:
            sess['email'] = self.user_email

        response = self.app.get('/daily_challenge')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Today's Challenges", response.data)

    def test_daily_challenge_display(self):
        # Simulate a logged-in user
        with self.app.session_transaction() as sess:
            sess['email'] = self.user_email

        response = self.app.get('/daily_challenge')
        challenges = [
            b"Drink 8 glasses of water",
            b"Walk 5,000 steps",
            b"Avoid sugary drinks",
            b"Eat at least 3 servings of vegetables",
            b"Complete a 15-minute meditation",
            b"Do a 30-minute workout",
            b"Sleep for at least 7 hours"
        ]
        self.assertTrue(
            any(challenge in response.data for challenge in challenges)
        )

    def test_mark_challenge_completed(self):
        # Simulate a logged-in user
        with self.app.session_transaction() as sess:
            sess['email'] = self.user_email

        # Get today's challenges
        today = datetime.today().strftime('%Y-%m-%d')
        random.seed(today)
        DAILY_CHALLENGES = [
            "Drink 8 glasses of water",
            "Walk 5,000 steps",
            "Avoid sugary drinks",
            "Eat at least 3 servings of vegetables",
            "Complete a 15-minute meditation",
            "Do a 30-minute workout",
            "Sleep for at least 7 hours"
        ]
        daily_challenges = random.sample(DAILY_CHALLENGES, 3)
        challenge_to_complete = daily_challenges[0]

        # Post to mark the challenge as completed
        response = self.app.post(
            '/daily_challenge',
            data={'completed_challenge': challenge_to_complete},
            follow_redirects=True
        )

        # Check that the challenge is marked as completed in the database
        user_data = mongo.db.users.find_one({'email': self.user_email})
        completed_challenges = user_data.get('completed_challenges', {})
        self.assertIn(
            f"{today}_{challenge_to_complete}",
            completed_challenges
        )
        self.assertTrue(
            completed_challenges[f"{today}_{challenge_to_complete}"]
        )

        # Decode response data to string and unescape HTML entities
        response_text = response.data.decode('utf-8')
        response_text_unescaped = html.unescape(response_text)
        expected_message = (
            f"Challenge '{challenge_to_complete}' completed! Great job!"
        )

        # Uncomment the following lines if you want
        # to print response data for debugging
        # if expected_message not in response_text_unescaped:
        #     print("Response data:", response_text_unescaped)
        #     print("Expected message:", expected_message)

        self.assertIn(expected_message, response_text_unescaped)

    def test_all_challenges_completed(self):
        # Simulate a logged-in user
        with self.app.session_transaction() as sess:
            sess['email'] = self.user_email

        # Get today's challenges
        today = datetime.today().strftime('%Y-%m-%d')
        random.seed(today)
        DAILY_CHALLENGES = [
            "Drink 8 glasses of water",
            "Walk 5,000 steps",
            "Avoid sugary drinks",
            "Eat at least 3 servings of vegetables",
            "Complete a 15-minute meditation",
            "Do a 30-minute workout",
            "Sleep for at least 7 hours"
        ]
        daily_challenges = random.sample(DAILY_CHALLENGES, 3)

        # Mark all challenges as completed
        for challenge in daily_challenges:
            mongo.db.users.update_one(
                {"email": self.user_email},
                {
                    "$set": {
                        f"completed_challenges.{today}_{challenge}": True
                    }
                },
                upsert=True
            )

        response = self.app.get('/daily_challenge')

        # Check that the shareable message is displayed
        response_text = response.data.decode('utf-8')
        shareable_message = (
            "I completed all my daily challenges today! "
            "Feeling great and staying on track with #CalorieApp."
        )

        self.assertIn(shareable_message, response_text)

        # Check that social share buttons are displayed
        self.assertIn('Share on Twitter', response_text)
        self.assertIn('Share on Facebook', response_text)

    def test_daily_challenge_access_without_login(self):
        # Clear the session to simulate a user not logged in
        with self.app.session_transaction() as sess:
            sess.clear()
            # Uncomment for debugging
            # print("Session after clearing:", dict(sess))

        response = self.app.get('/daily_challenge', follow_redirects=False)
        # Uncomment for debugging
        # print("Response status code:", response.status_code)
        # print("Response headers:", response.headers)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])


if __name__ == '__main__':
    unittest.main()
