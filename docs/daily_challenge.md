# Daily_Challenge route

The `/daily_challenge` route in this Flask application assigns users three random fitness tasks from a curated list each day, enhancing engagement and providing a diverse workout experience. The challenges are tracked in the MongoDB database to record completion status and offer personalized feedback. Once all challenges are completed, a shareable message with a social media prompt is generated, allowing users to share their achievements with others.
## Route Details

- **Route Path:** `/daily_challenge`
- **Methods:** GET, POST

## Code Explanation

1. **Rendering the Template:**
   - The route renders the `daily_challenge.html	` template when accessed. 

## Usage Instructions

1. Users can access the daily challenge page by navigating to in their web browser.
2. The page has 3 random tasks generated which user can mark as completed.
3. The user when marks all 3 task as completed a shareable message is generated with an option to share to the social media.

## Further Considerations

- Ensure that the logic for social sharing is created in a separate function which can be implemented in this.
  
