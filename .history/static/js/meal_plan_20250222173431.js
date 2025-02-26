/**
 * Handles form submission for meal plan recommendation, preventing page reload.
 * @param {Event} event - The form submission event
 */
function getMealPlan(event) {
    // Prevents the default form submission which would reload the page
    event.preventDefault();

    // Fetching values from the form inputs
    const goal = $("#goal").val(); // User's goal: Weight Loss, Muscle Gain, or Maintenance
    const calories = parseInt($("#calories").val()); // Calorie target entered by the user
    const protein = parseInt($("#protein").val()); // Protein target in grams entered by the user
    const carbs = parseInt($("#carbs").val()); // Carbohydrate target in grams entered by the user
    const fat = parseInt($("#fat").val()); // Fat target in grams entered by the user

    // Logging the request details for debugging purposes
    console.log("Requesting meal plan with:", { goal, calories, protein, carbs, fat });

    // Making an AJAX POST request to the backend to fetch the recommended meal plan
    $.ajax({
        type: "POST", // HTTP request method
        url: "/recommend_meal_plan", // Backend endpoint for meal recommendation
        contentType: "application/json", // Data format being sent to the server
        data: JSON.stringify({ goal, calories, protein, carbs, fat }), // Converting the data to JSON string format
        success: function(response) {
            // Logging the response from the server for debugging
            console.log("Meal plan response:", response);

            // Calling the function to display the meal plan on the page
            displayMealPlan(response);
        },
        error: function(xhr, status, error) {
            // Logging any error if the AJAX request fails
            console.log("Error fetching meal plan:", xhr.status, xhr.responseText);
            
            // Displaying an alert to the user in case of an error
            alert("There was an error fetching your meal plan. Please try again.");
        }
    });
}

/**
 * Renders the recommended meal plan in the specified HTML container.
 * @param {Array} meals - Array of meal objects returned from the server.
 */
function displayMealPlan(meals) {
    // Selecting the container where the meal plan will be displayed
    const mealContainer = $("#meal-plan-result");
    
    // Clearing any existing content in the container to avoid duplication
    mealContainer.empty();

    // Check if meals data exists and is not empty
    if (meals && meals.length > 0) {
        // Loop through each meal in the array and create an HTML structure for it
        meals.forEach((meal, index) => {
            // HTML structure for each meal card
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
            
            // Appending the created meal HTML structure to the meal container
            mealContainer.append(mealHTML);
        });
    } else {
        // Displaying a message if no meals are found
        mealContainer.append("<p>No meals found for your preferences.</p>");
    }
}

/**
 * jQuery ready function to ensure the document is fully loaded before running scripts.
 * Checks if the current page is the meal plan page and triggers the getMealPlan function.
 */
$(document).ready(function() {
    // Checks if the user is on the meal plan page
    if (window.location.pathname === "/meal_plan") {
        getMealPlan(); // Automatically fetches the meal plan on page load
    }
});
