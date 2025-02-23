/**
 * Renders the recommended meal plan in the specified HTML container.
 * Each card has two columns: left for text details (with score) and right for a fixed-size image and a guide button.
 * @param {Array} meals - Array of meal objects returned from the server.
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
                            <a class="btn btn-primary mt-2" href="/meal_guide?food_name=${encodeURIComponent(meal.food_name || '')}&calories=${meal.calories}&protein=${meal.protein}&carbs=${meal.carbs}&fat=${meal.fat}&cook_guide=${encodeURIComponent(meal.cook_guide)}" target="_blank">Guide</a>
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
