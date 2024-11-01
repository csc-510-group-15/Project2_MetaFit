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
    result = recommend_meal_plan("Muscle Gain", 450, 35, 55, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_high_calorie_edge_case(setup_model):
    result = recommend_meal_plan("Muscle Gain", 500, 40, 70, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_valid_carbohydrate_intake(setup_model):
    result = recommend_meal_plan("Muscle Gain", 400, 35, 60, 10)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


# Non-Nominal Test Cases
def test_invalid_goal_input(setup_model):
    with pytest.raises(ValueError):
        recommend_meal_plan("Invalid Goal", 250, 5, 45, 5)


def test_negative_calorie_value(setup_model):
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", -100, 5, 45, 5)


def test_zero_fat_input_for_muscle_gain(setup_model):
    result = recommend_meal_plan("Muscle Gain", 500, 40, 50, 0)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_low_protein_for_weight_loss(setup_model):
    result = recommend_meal_plan("Weight Loss", 300, 5, 30, 10)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_calories_at_lower_limit_for_weight_loss(setup_model):
    result = recommend_meal_plan("Weight Loss", 200, 10, 30, 5)
    assert any(meal['goal'] == "Weight Loss" for meal in result)


def test_high_protein_for_muscle_gain(setup_model):
    result = recommend_meal_plan("Muscle Gain", 600, 80, 50, 30)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_realistic_values(setup_model):
    result = recommend_meal_plan("Muscle Gain", 550, 45, 60, 15)
    assert any(meal['goal'] == "Muscle Gain" for meal in result)


def test_non_numeric_protein_value(setup_model):
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", 250, "ten", 45, 5)


def test_sql_injection_in_inputs(setup_model):
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", "250; DROP TABLE meals;", 5, 45, 5)


def test_empty_input_fields(setup_model):
    with pytest.raises(ValueError):
        recommend_meal_plan("", "", "", "", "")
