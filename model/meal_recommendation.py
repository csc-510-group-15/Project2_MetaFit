import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# Load CSV data
meal_data = pd.read_csv('food_data/meal_plan_data.csv')


# Data Preprocessing based on goals
def preprocess_data():
    # Adding a 'goal' column based on calorie values
    meal_data['goal'] = meal_data['calories'].apply(
        lambda x: 'Weight Loss'
        if x <= 300 else ('Muscle Gain' if x >= 400 else 'Maintenance'))

    # Selecting features and normalizing them
    features = meal_data[['calories', 'protein', 'carbs', 'fat']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    return scaled_features, meal_data['goal']


# Initialize and train the model
def train_model():
    X, y = preprocess_data()
    knn_model = KNeighborsClassifier(n_neighbors=5)
    knn_model.fit(X, y)
    return knn_model


# Train the model once
model = train_model()


# Recommendation function
def recommend_meal_plan(goal, calories, protein, carbs, fat):
    # Preprocess user input
    scaler = StandardScaler()
    input_data = scaler.fit_transform([[calories, protein, carbs, fat]])

    # Predict the goal using the trained model
    prediction = model.predict(input_data)

    # Filter meals based on the predicted goal
    recommended_meals = meal_data[meal_data['goal'] == prediction[0]].to_dict(
        orient='records')
    return recommended_meals
