import unittest
from application import app, mongo


class FriendsRouteTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

        # Push an application context
        self.app_context = app.app_context()
        self.app_context.push()

        # Clear the collections used
        mongo.db.user.delete_many({})
        mongo.db.friends.delete_many({})

        # Insert test users
        mongo.db.user.insert_many([
            {
                'name': 'Alice',
                'email': 'alice@example.com',
                'burn_rate': 500,
                'target_date': '2023-12-31'
            },
            {
                'name': 'Bob',
                'email': 'bob@example.com',
                'burn_rate': -300,
                'target_date': '2023-11-30'
            },
            {
                'name': 'Charlie',
                'email': 'charlie@example.com',
                'burn_rate': 0,
                'target_date': '2024-01-15'
            },
        ])

        # Simulate a logged-in user (Alice)
        with self.app.session_transaction() as sess:
            sess['email'] = 'alice@example.com'

    def tearDown(self):
        # Remove test data
        mongo.db.user.delete_many({})
        mongo.db.friends.delete_many({})
        self.app_context.pop()

    def test_friends_route_access(self):
        response = self.app.get('/friends')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Friends', response.data)

    def test_no_friends_display(self):
        response = self.app.get('/friends')
        self.assertNotIn(b'<span>Alice</span>', response.data)

    def test_add_friends_display(self):
        response = self.app.get('/friends')
        self.assertIn(b'Bob', response.data)
        self.assertIn(b'Charlie', response.data)

    def test_send_friend_request(self):
        # Simulate sending a friend request to Bob
        mongo.db.friends.insert_one({
            'sender': 'alice@example.com',
            'receiver': 'bob@example.com',
            'accept': False
        })
        response = self.app.get('/friends')
        self.assertIn(b'Sent Requests', response.data)
        self.assertIn(b'bob@example.com', response.data)

    def test_pending_approvals(self):
        # Simulate Bob sending a friend request to Alice
        mongo.db.friends.insert_one({
            'sender': 'bob@example.com',
            'receiver': 'alice@example.com',
            'accept': False
        })
        response = self.app.get('/friends')
        self.assertIn(b'Pending Approvals', response.data)
        self.assertIn(b'bob@example.com', response.data)
        # Check the flash message
        self.assertIn(b'You have 1 pending friend requests.', response.data)

    def test_shareable_message_positive_burn_rate(self):
        response = self.app.get('/friends')
        expected_message = (
            "I’m working hard to gain 500 calories daily to reach "
            "my goal by 2023-12-31! #CalorieApp"
        ).encode('utf-8')
        self.assertIn(expected_message, response.data)

    def test_shareable_message_negative_burn_rate(self):
        # Change Alice's burn_rate to negative
        mongo.db.user.update_one(
            {'email': 'alice@example.com'},
            {'$set': {'burn_rate': -400}}
        )
        response = self.app.get('/friends')
        expected_message = (
            "Burning 400 calories daily to stay on track for my goal "
            "by 2023-12-31! #CalorieApp"
        ).encode('utf-8')
        self.assertIn(expected_message, response.data)

    def test_shareable_message_zero_burn_rate(self):
        # Change Alice's burn_rate to zero
        mongo.db.user.update_one(
            {'email': 'alice@example.com'},
            {'$set': {'burn_rate': 0}}
        )
        response = self.app.get('/friends')
        expected_message = (
            "Burning 0 calories daily to stay on track for my goal "
            "by 2023-12-31! #CalorieApp"
        ).encode('utf-8')
        self.assertIn(expected_message, response.data)

    def test_social_media_share_links(self):
        response = self.app.get('/friends')
        self.assertIn(b'Share on Twitter', response.data)
        self.assertIn(b'Share on Facebook', response.data)


if __name__ == '__main__':
    unittest.main()
