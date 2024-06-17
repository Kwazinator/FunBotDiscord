# Discord Bot Commands

## Commands

### /ping
- **Description**: Responds with "pong".
- **Usage**: `/ping`

### /reminder
- **Description**: Sets a reminder for a specified time.
- **Usage**: `/reminder <time> "<message>"`
- **Example**: `/reminder 2 days 1 hour "Hello World"`
  - **Note**: The time can be specified in days, hours, or minutes. message must be wrapped in quotes

## Bot Behavior
- Responds to `hello` with a greeting mentioning the user.
- Responds to `hey jared` with a playful message.
- Adds thumbs up and thumbs down reactions to messages containing `??`.

## Background Tasks
- **check_due_reminders**: Checks for due reminders every minute and sends the reminder message to the specified channel.
