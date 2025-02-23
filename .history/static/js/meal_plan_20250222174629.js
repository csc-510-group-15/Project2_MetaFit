/**
 * Handles form submission for meal plan recommendation.
 */
function getMealPlan(event) {
    event.preventDefault();

    const goal = $("#goal").val();
    const calories = parseInt($("#calories").val());
    const protein = parseInt($("#protein").val());
    const carbs = parseInt($("#carbs").val());
    const fat = parseInt($("#fat").val());

    // Validate numeric inputs
    if (isNaN(calories) || isNaN(protein) || isNaN(carbs) || isNaN(fat)) {
        alert("Please enter valid numeric values for calories, protein, carbs, and fat.");
        return;
    }

    console.log("Requesting meal plan with:", { goal, calories, protein, carbs, fat });

    $.ajax({
        type: "POST",
        url: "/recommend_meal_plan",
        contentType: "application/json",
        data: JSON.stringify({ goal, calories, protein, carbs, fat }),
        success: function(response) {
            console.log("Meal plan response:", response);
            displayMealPlan(response);
        },
        error: function(xhr, status, error) {
            console.log("Error fetching meal plan:", xhr.status, xhr.responseText);
            alert("There was an error fetching your meal plan. Please try again.");
        }
    });
}

/**
 * Renders the recommended meal plan.
 */
function displayMealPlan(meals) {
    const mealContainer = $("#meal-plan-result");
    mealContainer.empty();

    if (meals && meals.length > 0) {
        meals.forEach((meal, index) => {
            const mealHTML = `
                <div class="card mb-3">
                    <div class="row no-gutters">
                        <!-- Left Column: Meal Details -->
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">Meal ${index + 1}: ${meal.food_name || "No name available"} - Score: ${meal.score}</h5>
                                <p class="card-text"><strong>Calories:</strong> ${meal.calories}</p>
                                <p class="card-text"><strong>Protein:</strong> ${meal.protein}g</p>
                                <p class="card-text"><strong>Carbs:</strong> ${meal.carbs}g</p>
                                <p class="card-text"><strong>Fat:</strong> ${meal.fat}g</p>
                            </div>
                        </div>
                        <!-- Right Column: Image and Guide Button -->
                        <div class="col-md-4 d-flex flex-column align-items-center justify-content-center">
                            <img src="${meal.image_url}" alt="${meal.food_name || 'Meal Image'}" style="width:150px; height:150px; object-fit:cover;">
                            <a class="btn btn-primary mt-2" 
                               href="/meal_guide?food_name=${encodeURIComponent(meal.food_name || '')}&calories=${meal.calories}&protein=${meal.protein}&carbs=${meal.carbs}&fat=${meal.fat}&cook_guide=${encodeURIComponent(meal.cook_guide)}&image_url=${encodeURIComponent(meal.image_url)}" 
                               target="_blank">Guide</a>
                        </div>
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
    // Optionally, auto-fetch on page load:
    // if (window.location.pathname === "/meal_plan") getMealPlan(new Event('load'));
});
