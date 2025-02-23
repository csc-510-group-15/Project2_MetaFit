/**
 * Handles form submission for meal plan recommendation.
 * @param {Event} event - The form submission event.
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
 * Renders the recommended meal plan as 5 boxes in one line.
 * Each box displays:
 *   - Meal number, name, and score
 *   - Calories, Protein, Carbs, Fat on separate lines
 *   - A "Guide" button at the bottom linking to the guide page.
 * @param {Array} meals - Array of meal objects returned from the server.
 */
function displayMealPlan(meals) {
    const mealContainer = $("#meal-plan-result");
    mealContainer.empty();

    if (meals && meals.length > 0) {
        // Create a flex container for the cards.
        let rowHTML = `<div class="d-flex flex-wrap justify-content-between">`;
        meals.forEach((meal, index) => {
            // Build each card with minimal content.
            const cardHTML = `
                <div class="card mb-3" style="flex: 0 0 18%; margin-bottom: 20px; text-align: center;">
                    <div class="card-body p-2">
                        <h6 class="card-title">Meal ${index + 1}: ${meal.food_name || "No name available"} - Score: ${meal.score}</h6>
                        <p class="card-text mb-1"><strong>Calories:</strong> ${meal.calories}</p>
                        <p class="card-text mb-1"><strong>Protein:</strong> ${meal.protein}g</p>
                        <p class="card-text mb-1"><strong>Carbs:</strong> ${meal.carbs}g</p>
                        <p class="card-text mb-1"><strong>Fat:</strong> ${meal.fat}g</p>
                        <a class="btn btn-primary btn-sm mt-2" 
                            href="/meal_guide?food_name=${encodeURIComponent(meal.food_name || '')}&calories=${meal.calories}&protein=${meal.protein}&carbs=${meal.carbs}&fat=${meal.fat}&cook_guide=${encodeURIComponent(meal.cook_guide)}&image_url=${encodeURIComponent(meal.image_url)}" 
                            target="_blank">Guide</a>
                    </div>
                </div>
            `;
            rowHTML += cardHTML;
        });
        rowHTML += `</div>`;
        mealContainer.append(rowHTML);
    } else {
        mealContainer.append("<p>No meals found for your preferences.</p>");
    }
}

$(document).ready(function() {
    // Auto-fetch on page load if desired.
    // if (window.location.pathname === "/meal_plan") getMealPlan(new Event('load'));
});
