# Friends route

The `/friends` route in this Flask application is an existing route with a new additional features feature enables users to broadcast their fitness milestones directly to social media platforms. It generates a dynamic, shareable message based on each user’s specific progress metrics, like calories burned or challenges completed.

## Route Details

- **Route Path:** `/friends`
- **Methods:** GET

## Code Explanation

1. **Rendering the Template:**
   - The route renders the `friends.html` template when accessed. 

## Usage Instructions

1. Users can access the friends page by navigating to in their web browser.
2. The page has a “Share Your Achievements on Social Media” division which will generate a shareable message as per user progress which can be shared to Twitter and Facebook.

## Further Considerations

- Ensure that the logic for social sharing (possibly in a separate function or module) is correctly implemented and integrated with this route.
- Confirm that the connection to the data source (e.g., database or API) is properly configured and established.
- Customize the shareable message generation as per the new features.

