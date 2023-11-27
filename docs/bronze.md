# Bronze List Route

This Flask application route, `/bronze_list`, is designed to display the bronze list for the current day. It utilizes a form (`getDate`) to allow users to select a target date, and upon form submission, it retrieves the corresponding bronze list from the MongoDB database.

## Route Details

- **Route Path:** `/bronze_list`
- **Methods:** GET, POST

## Code Explanation

1. **Form Handling:**
   - The route begins by initializing a form object (`getDate`) for users to input the target date.

2. **Form Submission:**
   - On a POST request and successful form validation, the selected target date is retrieved.
   - A query is made to the MongoDB database to find the bronze list for the specified date.

3. **Database Interaction:**
   - If a bronze list document exists for the target date, the existing list is retrieved and updated.
   - If no document exists for the date, a new document is created with an empty list of users.

4. **Rendering the Template:**
   - The route renders the 'bronze_list.html' template, passing the form, title, and the list of bronze users.
