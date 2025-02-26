import pandas as pd
import numpy as np
import random
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# Load CSV data
meal_data = pd.read_csv('food_data/meal_plan_data.csv')

# Ensure image_url and cook_guide columns exist; if not, create placeholders.
if 'image_url' not in meal_data.columns:
    meal_data['image_url'] = 'https://via.placeholder.com/150'
if 'cook_guide' not in meal_data.columns:
    meal_data['cook_guide'] = 'Ingredients: N/A\nInstructions: N/A'

# Initialize scaler globally
scaler = StandardScaler()

def preprocess_data():
    """
    Preprocesses the meal data for model training.
    Adds a 'goal' column to classify each meal based on its calorie value:
      - 'Weight Loss' if calories <= 300
      - 'Muscle Gain' if calories >= 400
      - 'Maintenance' otherwise
    Normalizes the selected features (calories, protein, carbs, fat)
    using StandardScaler.
    """
    meal_data['goal'] = meal_data['calories'].apply(
        lambda x: 'Weight Loss' if x <= 300 else ('Muscle Gain' if x >= 400 else 'Maintenance')
    )
    features = meal_data[['calories', 'protein', 'carbs', 'fat']]
    global scaler
    scaled_features = scaler.fit_transform(features)
    return scaled_features, meal_data['goal']

def train_model():
    X, y = preprocess_data()
    knn_model = KNeighborsClassifier(n_neighbors=5)
    knn_model.fit(X, y)
    return knn_model

# Train the model once
model = train_model()

def recommend_meal_plan(goal, calories, protein, carbs, fat, top_n=5):
    """
    Recommends meals from the dataset that match the user's dietary goal and
    macro-nutrient preferences. Returns only the top_n (default 5) meals.
    Each recommended meal is assigned a unique score above 90.
    """
    # Validate input
    if goal not in ["Weight Loss", "Muscle Gain", "Maintenance"]:
        raise ValueError("Invalid dietary goal. Choose from 'Weight Loss', 'Muscle Gain', or 'Maintenance'.")
    if not isinstance(calories, (int, float)) or not isinstance(protein, (int, float)) or \
       not isinstance(carbs, (int, float)) or not isinstance(fat, (int, float)):
        raise ValueError("Caloric and macronutrient values must be numeric.")
    if calories < 0 or protein < 0 or carbs < 0 or fat < 0:
        raise ValueError("Caloric and macronutrient values must be non-negative.")
    
    # Prepare input vector as a DataFrame with matching feature names
    input_df = pd.DataFrame([[calories, protein, carbs, fat]],
                            columns=['calories', 'protein', 'carbs', 'fat'])
    input_data = scaler.transform(input_df)
    
    # Predict the dietary goal using the trained model
    prediction = model.predict(input_data)
    
    # Filter meals based on the predicted goal
    subset = meal_data[meal_data['goal'] == prediction[0]].copy()
    
    # Compute Euclidean distance for ranking meals
    input_vector = input_data[0]
    def compute_distance(row):
        row_df = pd.DataFrame([[row['calories'], row['protein'], row['carbs'], row['fat']]],
                              columns=['calories', 'protein', 'carbs', 'fat'])
        meal_vector = scaler.transform(row_df)[0]
        return np.linalg.norm(input_vector - meal_vector)
    
    subset['distance'] = subset.apply(compute_distance, axis=1)
    subset_sorted = subset.sort_values(by='distance')
    
    # Take top_n meals
    recommended_meals = subset_sorted.head(top_n).to_dict(orient='records')
    
    # Assign a unique random score (all above 90) to each recommended meal
    scores = random.sample(range(91, 101), top_n)
    for i, meal in enumerate(recommended_meals):
        meal['score'] = scores[i]
    
    return recommended_meals
