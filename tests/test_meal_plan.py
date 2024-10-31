import pytest
from unittest.mock import patch
import pandas as pd
from model.meal_recommendation import recommend_meal_plan, train_model

# Mock dataset for testing
mock_data = pd.DataFrame({
    'calories': [250, 150, 300, 450, 500],
    'protein': [5, 10, 25, 35, 40],
    'carbs': [45, 15, 35, 55, 60],
    'fat': [5, 5, 10, 15, 20],
    'goal': ['Weight Loss', 'Weight Loss', 'Maintenance', 'Muscle Gain', 'Muscle Gain'],
    'food_name': ['Oatmeal with Berries', 'Greek Yogurt', 'Grilled Chicken Salad', 'Protein Shake', 'Steak']
})

@pytest.fixture(scope="module")
def setup_model():
    # Mock pd.read_csv so that it returns mock_data instead of reading a file
    with patch('model.meal_recommendation.pd.read_csv', return_value=mock_data):
        model = train_model()
    return model

def test_valid_weight_loss_meal(setup_model):
    """Test a valid meal recommendation for weight loss."""
    result = recommend_meal_plan("Weight Loss", 250, 5, 45, 5)
    assert result[0]['goal'] == "Weight Loss"

def test_valid_muscle_gain_meal(setup_model):
    """Test a valid meal recommendation for muscle gain."""
    result = recommend_meal_plan("Muscle Gain", 450, 35, 55, 15)
    assert result[0]['goal'] == "Muscle Gain"

def test_valid_maintenance_meal(setup_model):
    """Test a valid meal recommendation for maintenance."""
    result = recommend_meal_plan("Maintenance", 300, 25, 35, 10)
    assert result[0]['goal'] == "Maintenance"

def test_low_calorie_edge_case(setup_model):
    """Test an edge case with low calorie values."""
    result = recommend_meal_plan("Weight Loss", 0, 0, 0, 0)
    assert len(result) == 0

def test_high_calorie_edge_case(setup_model):
    """Test an edge case with high calorie values."""
    result = recommend_meal_plan("Muscle Gain", 1000, 100, 100, 100)
    assert all(meal['goal'] == "Muscle Gain" for meal in result)

def test_missing_protein_value(setup_model):
    """Test a case with missing protein input."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Maintenance", 300, None, 35, 10)

def test_negative_protein_value(setup_model):
    """Test a case with negative protein input."""
    result = recommend_meal_plan("Weight Loss", 250, -5, 45, 5)
    assert len(result) == 0

def test_non_numeric_protein_value(setup_model):
    """Test a case with non-numeric protein input."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Weight Loss", 250, "ten", 45, 5)

def test_high_fat_edge_case(setup_model):
    """Test an edge case with high fat value."""
    result = recommend_meal_plan("Muscle Gain", 450, 35, 55, 100)
    assert all(meal['goal'] == "Muscle Gain" for meal in result)

def test_low_fat_edge_case(setup_model):
    """Test an edge case with zero fat value."""
    result = recommend_meal_plan("Weight Loss", 250, 5, 45, 0)
    assert all(meal['goal'] == "Weight Loss" for meal in result)

def test_invalid_goal_input(setup_model):
    """Test invalid goal input."""
    with pytest.raises(ValueError):
        recommend_meal_plan("Invalid Goal", 250, 5, 45, 5)
