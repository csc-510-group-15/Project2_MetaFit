# import pandas as pd
# from sklearn.preprocessing import LabelEncoder, StandardScaler
# from sklearn.neighbors import NearestNeighbors
# from sklearn.cluster import KMeans
# import numpy as np

# # Load the dataset
# # Replace with your file path
# data = pd.read_csv(r"megaGymDataset.csv")

# # Handle missing values in "Rating" (replace NaNs with the mean)
# data["Rating"] = data["Rating"].fillna(data["Rating"].mean())

# # Encode categorical variables
# label_encoders = {}
# for col in ["Type", "BodyPart", "Equipment", "Level"]:
#     le = LabelEncoder()
#     data[col] = le.fit_transform(data[col])
#     label_encoders[col] = le

# # Normalize numerical features
# scaler = StandardScaler()
# data["Rating"] = scaler.fit_transform(data[["Rating"]])

# # Prepare feature set for clustering and recommendations
# features = data[["Type", "BodyPart", "Equipment", "Level", "Rating"]]

# # Cluster exercises using K-Means
# kmeans = KMeans(n_clusters=3, random_state=42)
# data["Cluster"] = kmeans.fit_predict(features)

# # Build a Nearest Neighbors model for content-based recommendations
# nn_model = NearestNeighbors(n_neighbors=3, metric='euclidean')
# nn_model.fit(features)

# # User profile (Example Input)
# user_input = {
#     "Type": "Strength",
#     "BodyPart": "Abdominals",  # Adjust to your dataset values
#     "Equipment": "Bands",
#     "Level": "Intermediate",
#     "Rating": 4.5,  # Adjust based on normalized value
# }

# # Transform user input to match feature space
# user_vector = [
#     label_encoders["Type"].transform([user_input["Type"]])[0],
#     label_encoders["BodyPart"].transform([user_input["BodyPart"]])[0],
#     label_encoders["Equipment"].transform([user_input["Equipment"]])[0],
#     label_encoders["Level"].transform([user_input["Level"]])[0],
#     scaler.transform([[user_input["Rating"]]])[0][0],
# ]

# # Get recommendations
# distances, indices = nn_model.kneighbors([user_vector])
# recommended_exercises = data.iloc[indices[0]]

# # Display recommendations
# print("Recommended Exercises:")
# for _, row in recommended_exercises.iterrows():
#     print(f"- {row['Title']} ({row['Rating']:.2f} stars): {row['Desc']}")

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# Load the dataset
data = pd.read_csv("megaGymDataset.csv")  # Replace with your file path

data["Rating"] = data["Rating"].fillna(data["Rating"].mean())
data['OriginalRating'] = data['Rating']

scaler = StandardScaler()
data["Rating"] = scaler.fit_transform(data[["Rating"]])

# Encode categorical variables
label_encoders = {}
for col in ["Type", "BodyPart", "Equipment", "Level"]:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Normalize numerical features
scaler = StandardScaler()
data["Rating"] = scaler.fit_transform(data[["Rating"]])

# Prepare feature set for clustering and recommendations
features = data[["Type", "BodyPart", "Equipment", "Level", "Rating"]]

# Cluster exercises using K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
data["Cluster"] = kmeans.fit_predict(features)

# Build a Nearest Neighbors model for content-based recommendations
nn_model = NearestNeighbors(n_neighbors=3, metric='euclidean')
nn_model.fit(features)

# User profile (Example Input)
user_input = {
    "Type": "Strength",
    "BodyPart": "Abdominals",  # Adjust to your dataset values
    "Equipment": "Bands",
    "Level": "Intermediate",
    "Rating": 4.5,  # Adjust based on normalized value
}

# Transform user input to match feature space
user_vector = [
    label_encoders["Type"].transform([user_input["Type"]])[0],
    label_encoders["BodyPart"].transform([user_input["BodyPart"]])[0],
    label_encoders["Equipment"].transform([user_input["Equipment"]])[0],
    label_encoders["Level"].transform([user_input["Level"]])[0],
    scaler.transform([[user_input["Rating"]]])[0][0],
]

# Get recommendations
distances, indices = nn_model.kneighbors([user_vector])
recommended_exercises = data.iloc[indices[0]]

# Display recommendations
print("Recommended Exercises:")
for _, row in recommended_exercises.iterrows():
    print(f"- {row['Title']} ({row['OriginalRating']:.2f} stars): {row['Desc']}")
