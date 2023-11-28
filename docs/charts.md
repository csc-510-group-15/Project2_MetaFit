# Chart Visualization and Progress Feedback

This web page, built using Flask and incorporating Chart.js, provides users with visual representations of their caloric progress over the past 7 days. It also offers personalized feedback based on their progress towards a caloric goal.

## Key Features

### 1. Progress Feedback

A dynamic alert at the top of the page delivers encouraging messages based on the user's caloric progress. The message adapts to whether the user needs to gain or burn calories to achieve their goal by a specified target date.

### 2. Chart Visualization

The page includes an interactive chart that visualizes the net calories consumed or burned over the past 7 days. Users can select different chart types (Bar Chart, Pie Chart, Line Chart, Radar Chart, Doughnut Chart, Bubble Chart, etc.) using the dropdown menu.

### 3. Chart Customization

The chart's color scheme adapts to the user's goal, highlighting calorie gains or burns. Positive values are represented with green shades, while negative values are depicted in varying shades of red. This provides a quick visual indication of progress.

## Implementation Details

### 1. Progress Feedback Logic

- The alert message dynamically adjusts based on the user's caloric goal and progress.
- The `burn_rate` variable determines whether the user needs to gain or burn calories.
- The `target_date` variable displays the date by which the user should achieve their goal.

### 2. Chart Visualization

- The Chart.js library is utilized to create an interactive chart.
- The chart type can be selected using the dropdown menu, triggering an update of the displayed chart.
- The `labels` and `values` variables provide the data for the X-axis labels and Y-axis values, respectively.

### 3. Chart Customization

- The chart's color scheme is adapted to the user's goal using the `isBurn` variable.
- Positive values are highlighted in green shades for gains and red shades for burns.
- Negative values are displayed in varying shades of red for gains and green shades for burns.

## Instructions

1. Ensure that the Flask application is properly set up and configured.
2. Include the necessary dependencies in your project.
3. Copy the provided HTML template into your Flask application's template folder.
4. Configure the template to integrate with your data sources, such as the `burn_rate`, `target_date`, `labels`, and `values` variables.
5. Run your Flask application and navigate to the page corresponding to this template.

## Further Customization

Feel free to customize the template to suit your specific requirements. Adjust the chart types, color schemes, and feedback messages to align with the goals and preferences of your users. Additionally, explore the Chart.js documentation for more advanced customization options.

**Note:** Ensure that the Chart.js library is included and properly linked in your project for the chart functionality to work correctly.
