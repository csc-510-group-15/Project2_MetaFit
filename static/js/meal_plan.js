function getMealPlan(event) {
    event.preventDefault(); // Prevent form submission reload

    // Fetching values from the form inputs
    const goal = $("#goal").val();
    const calories = parseInt($("#calories").val());
    const protein = parseInt($("#protein").val());
    const carbs = parseInt($("#carbs").val());
    const fat = parseInt($("#fat").val());

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

function displayMealPlan(meals) {
    const mealContainer = $("#meal-plan-result");
    mealContainer.empty();

    // Check if meals data exists and is not empty
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
                        <p class="card-text"><strong>Food Name:</strong> ${meal.food_name || "No name available"}</p>
                    </div>
                </div>
            `;
            mealContainer.append(mealHTML);
        });
    } else {
        mealContainer.append("<p>No meals found for your preferences.</p>");
    }
}
