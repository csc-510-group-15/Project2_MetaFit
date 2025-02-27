import unittest
from application import app


class ExerciseFinderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_valid_inputs(self):
        response = self.client.post(
            '/exercise', data={'muscle': 'biceps', 'difficulty': 'beginner'})
        content = response.data.decode()
        self.assertIn('Bicep Curl', content)
        # Check for "strength" case-insensitively:
        self.assertIn('strength', content.lower())

    def test_empty_muscle_input(self):
        response = self.client.post(
            '/exercise', data={'muscle': '', 'difficulty': 'beginner'})
        self.assertIn('Both muscle and difficulty are required!',
                      response.data.decode())

    def test_empty_difficulty_input(self):
        response = self.client.post(
            '/exercise', data={'muscle': 'biceps', 'difficulty': ''})
        self.assertIn('Both muscle and difficulty are required!',
                      response.data.decode())

    def test_error_message_display(self):
        response = self.client.post(
            '/exercise', data={'muscle': 'xyzmuscle', 'difficulty': 'intermediate'})
        self.assertIn(
            'No exercises found for the specified muscle and difficulty.', response.data.decode())

    def test_exercises_rendered(self):
        response = self.client.post(
            '/exercise', data={'muscle': 'biceps', 'difficulty': 'beginner'})
        content = response.data.decode()
        self.assertIn('Bicep Curl', content)
        self.assertIn('beginner', content.lower())
        self.assertIn('dumbbell', content.lower())

    def test_multiple_exercises_rendered(self):
        response = self.client.post(
            '/exercise', data={'muscle': 'triceps', 'difficulty': 'intermediate'})
        content = response.data.decode()
        # Adjust expected string to match rendered output: "triceps dip"
        self.assertIn('triceps dip', content.lower())
        self.assertIn('intermediate', content.lower())


if __name__ == '__main__':
    unittest.main()
