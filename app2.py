from flask import Flask, render_template, request, jsonify
from exercise import get_recommendations  # Import the function

app = Flask(__name__)


@app.route("/")
def index():
    body_parts = ['Abdominals', 'Adductors', 'Abductors', 'Biceps', 'Calves',
                  'Chest', 'Forearms', 'Glutes', 'Hamstrings', 'Lats', 'Lower Back',
                  'Middle Back', 'Traps', 'Neck', 'Quadriceps', 'Shoulders',
                  'Triceps']  # Example body parts
    levels = ['Beginner', 'Intermediate', 'Expert']  # Example levels
    return render_template("exercise.html", body_parts=body_parts, levels=levels)


@app.route("/recommend", methods=["POST"])
def recommend():
    # Get data from the form
    body_part = request.form.get("body_part")
    level = request.form.get("level")

    if not body_part or not level:
        return jsonify({"error": "Missing form data"}), 400

    # Call the recommendation function
    recommendations = get_recommendations(body_part, level)

    return jsonify(recommendations)  # Return the recommendations as JSON


if __name__ == "__main__":
    app.run(debug=True)
