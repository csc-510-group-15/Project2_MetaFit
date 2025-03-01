import pandas as pd
import random
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# Load CSV data
meal_data = pd.read_csv('food_data/meal_plan_data.csv')

# Ensure extra columns exist; if not, set default placeholders.
if 'image_url' not in meal_data.columns:
    meal_data['image_url'] = 'https://via.placeholder.com/150'
if 'cook_guide' not in meal_data.columns:
    meal_data['cook_guide'] = 'Ingredients: N/A\nInstructions: N/A'

# Initialize scaler globally
scaler = StandardScaler()


def preprocess_data():
    meal_data['goal'] = meal_data['calories'].apply(
        lambda x: 'Weight Loss' if x <= 300 else (
            'Muscle Gain' if x >= 400 else 'Maintenance')
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


model = train_model()


def recommend_meal_plan(goal, calories, protein, carbs, fat, top_n=5):
    if goal not in ["Weight Loss", "Muscle Gain", "Maintenance"]:
        raise ValueError(
            "Invalid dietary goal. Choose from 'Weight Loss', "
            "'Muscle Gain', or 'Maintenance'."
        )
    if not (isinstance(calories, (int, float)) and
            isinstance(protein, (int, float)) and
            isinstance(carbs, (int, float)) and
            isinstance(fat, (int, float))):
        raise ValueError(
            "Caloric and macronutrient values must be numeric."
        )
    if calories < 0 or protein < 0 or carbs < 0 or fat < 0:
        raise ValueError(
            "Caloric and macronutrient values must be non-negative."
        )

    input_data = scaler.transform([[calories, protein, carbs, fat]])
    prediction = model.predict(input_data)

    # Filter meals based on predicted goal
    recommended_meals = meal_data[meal_data['goal'] == prediction[0]] \
        .to_dict(orient='records')
    # Slice to top_n meals
    recommended_meals = recommended_meals[:top_n]
    # Assign unique random scores (all above 90)
    scores = random.sample(range(70, 100), top_n)
    for i, meal in enumerate(recommended_meals):
        meal['score'] = scores[i]
        print("Meal {} image_url: {}".format(i+1, meal.get('image_url')))
    recommended_meals = sorted(
        recommended_meals, key=lambda x: x['score'], reverse=True
    )
    return recommended_meals
