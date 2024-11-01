import pytest
from unittest.mock import patch
from model.meal_recommendation import recommend_meal_plan, train_model
import pandas as pd

# Mock dataset for testing
mock_data = [
    {
        'calories': 350,
        'protein': 30,
        'carbs': 20,
        'fat': 15,
        'goal': 'Maintenance'
    },
    {
        'calories': 250,
        'protein': 5,
        'carbs': 45,
        'fat': 5,
        'goal': 'Weight Loss'
    },
    {
        'calories': 400,
        'protein': 40,
        'carbs': 0,
        'fat': 25,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 500,
        'protein': 15,
        'carbs': 50,
        'fat': 20,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 600,
        'protein': 45,
        'carbs': 10,
        'fat': 30,
        'goal': 'Maintenance'
    },
    {
        'calories': 150,
        'protein': 10,
        'carbs': 15,
        'fat': 5,
        'goal': 'Weight Loss'
    },
    {
        'calories': 300,
        'protein': 25,
        'carbs': 35,
        'fat': 10,
        'goal': 'Maintenance'
    },
    {
        'calories': 250,
        'protein': 30,
        'carbs': 10,
        'fat': 15,
        'goal': 'Weight Loss'
    },
    {
        'calories': 400,
        'protein': 20,
        'carbs': 60,
        'fat': 10,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 350,
        'protein': 8,
        'carbs': 45,
        'fat': 20,
        'goal': 'Maintenance'
    },
    {
        'calories': 300,
        'protein': 10,
        'carbs': 50,
        'fat': 5,
        'goal': 'Weight Loss'
    },
    {
        'calories': 450,
        'protein': 35,
        'carbs': 55,
        'fat': 15,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 200,
        'protein': 10,
        'carbs': 40,
        'fat': 5,
        'goal': 'Weight Loss'
    },
    {
        'calories': 400,
        'protein': 15,
        'carbs': 30,
        'fat': 20,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 600,
        'protein': 50,
        'carbs': 40,
        'fat': 30,
        'goal': 'Maintenance'
    },
    {
        'calories': 500,
        'protein': 30,
        'carbs': 50,
        'fat': 20,
        'goal': 'Muscle Gain'
    },
    {
        'calories': 150,
        'protein': 15,
        'carbs': 30,
        'fat': 2,
        'goal': 'Weight Loss'
    },
    {
        'calories': 200,
        'protein': 20,
        'carbs': 20,
        'fat': 10,
        'goal': 'Weight Loss'
    },
    {
        'calories': 400,
        'protein': 30,
        'carbs': 40,
        'fat': 10,
        'goal': 'Maintenance'
    },
    {
        'calories': 600,
        'protein': 50,
        'carbs': 50,
        'fat': 25,
        'goal': 'Muscle Gain'
    },
]


@pytest.fixture(scope="module")
def setup_model():
    """Fixture to setup the KNN model with mock data."""
    with patch('model.meal_recommendation.pd.read_csv',
               return_value=pd.DataFrame(mock_data)):
        model = train_model()
    return model


# Nominal Test Cases
def test_valid_muscle_gain_recommendation(setup_model):
    """Test for valid muscle gain recommendation."""
    result = recommend_meal_plan("Muscle Gain", 450, 35, 55, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_high_calorie_edge_case(setup_model):
    """Test high calorie edge case for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 500, 40, 70, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_valid_carbohydrate_intake(setup_model):
    """Test for valid carbohydrate intake for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 400, 35, 60, 10)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


# Non-Nominal Test Cases
def test_invalid_goal_input(setup_model):
    """Test for invalid dietary goal input."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Invalid Goal", 250, 5, 45, 5)


def test_negative_calorie_value(setup_model):
    """Test for negative calorie value input."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", -100, 5, 45, 5)


def test_zero_fat_input_for_muscle_gain(setup_model):
    """Test for zero fat input for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 500, 40, 50, 0)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_low_protein_for_weight_loss(setup_model):
    """Test for low protein intake for weight loss."""
    result = recommend_meal_plan("Weight Loss", 300, 5, 30, 10)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_calories_at_lower_limit_for_weight_loss(setup_model):
    """Test for calories at lower limit for weight loss."""
    result = recommend_meal_plan("Weight Loss", 200, 10, 30, 5)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_high_protein_for_muscle_gain(setup_model):
    """Test for high protein intake for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 600, 80, 50, 30)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_realistic_values(setup_model):
    """Test for realistic calorie and macronutrient values."""
    result = recommend_meal_plan("Muscle Gain", 550, 45, 60, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_non_numeric_protein_value(setup_model):
    """Test for non-numeric protein value."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", 250, "ten", 45, 5)


def test_sql_injection_in_inputs(setup_model):
    """Test for SQL injection attempt in inputs."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", "250; DROP TABLE meals;", 5, 45, 5)


def test_empty_input_fields(setup_model):
    """Test for empty input fields."""
    with pytest.raises(ValueError):
        recommend_meal_plan("", "", "", "", "")


def test_valid_weight_loss_recommendation(setup_model):
    """Test for valid weight loss recommendation."""
    result = recommend_meal_plan("Weight Loss", 300, 20, 40, 10)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_valid_fat_intake_for_weight_loss(setup_model):
    """Test for valid fat intake for weight loss."""
    result = recommend_meal_plan("Weight Loss", 350, 25, 30, 10)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_high_calories_for_muscle_gain(setup_model):
    """Test for high calories for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 750, 60, 40, 30)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_calories_and_macros_positive(setup_model):
    """Test for positive calorie and macronutrient values."""
    result = recommend_meal_plan("Muscle Gain", 600, 40, 50, 20)
    assert len(result) > 0  # Expecting results for valid input


def test_edge_case_high_protein(setup_model):
    """Test for edge case of high protein intake."""
    result = recommend_meal_plan("Muscle Gain", 600, 100, 30, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_valid_carbs_for_weight_loss(setup_model):
    """Test for valid carbohydrate intake for weight loss."""
    result = recommend_meal_plan("Weight Loss", 300, 20, 40, 10)
    assert any(meal['goal'] == "Weight Loss"
               for meal in result)  # Expecting valid results


def test_minimum_protein_for_muscle_gain(setup_model):
    """Test for minimum protein intake for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 500, 20, 30, 15)
    assert any(meal['goal'] == "Muscle Gain"
               for meal in result)  # Expecting valid results
