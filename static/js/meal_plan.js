// meal_plan.js

function getMealPlan() {
    const goal = "weight loss"; // Replace with dynamic values if needed
    const calories = 2000;
    const protein = 150;
    const carbs = 200;
    const fat = 50;

    $.ajax({
        type: "POST",
        url: "/recommend_meal_plan",
        contentType: "application/json",
        data: JSON.stringify({ goal, calories, protein, carbs, fat }),
        success: function(response) {
            displayMealPlan(response);
        },
        error: function(xhr, status, error) {
            console.log("Error fetching meal plan:", error);
            alert("There was an error fetching your meal plan. Please try again.");
        }
    });
}

function displayMealPlan(meals) {
    const mealContainer = $("#meal-plan-container");
    mealContainer.empty();

    if (meals && meals.length > 0) {
        meals.forEach((meal, index) => {
            const mealHTML = `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Meal ${index + 1}</h5>
                        <p class="card-text"><strong>Calories:</strong> ${meal.calories}</p>
                        <p class="card-text"><strong>Protein:</strong> ${meal.protein}g</p>
                        <p class="card-text"><strong>Carbs:</strong> ${meal.carbs}g</p>
                        <p class="card-text"><strong>Fat:</strong> ${meal.fat}g</p>
                        <p class="card-text"><strong>Description:</strong> ${meal.description}</p>
                    </div>
                </div>
            `;
            mealContainer.append(mealHTML);
        });
    } else {
        mealContainer.append("<p>No meals found for your preferences.</p>");
    }
}

$(document).ready(function() {
    if (window.location.pathname === "/meal_plan") {
        getMealPlan();
    }
});
