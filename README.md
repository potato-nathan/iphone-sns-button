# SNS Button

Pythonista app for iPhone that sends notifications via Amazon SNS.

## Requirements

- Pythonista 3 for iOS
- Amazon SNS endpoint URL
- API token for authentication

## Setup

1. Copy `sns_button.py`, `.env`, and `distro_list.csv` to Pythonista
2. Edit `.env` with your configuration
3. Edit `distro_list.csv` with your recipient list
4. Run `sns_button.py`

## Configuration

### .env

```
SNS_ENDPOINT_URL=https://sns.us-east-1.amazonaws.com/your-topic-arn
SNS_API_TOKEN=your-api-token-here
BUTTON_NAME=Send Notification
DISTRO_LIST_CSV=distro_list.csv
CUSTOM_MESSAGE=Hello! This is a notification from the SNS Button app.
```

### distro_list.csv

```
First_Name,Last_Name,email,phone_number
John,Doe,john.doe@example.com,+15551234567
Jane,Smith,jane.smith@example.com,+15559876543
```

## API Request

Sends a POST request to your endpoint:

```json
{
    "message": "Your custom message here",
    "recipients": [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+15551234567"
        }
    ],
    "timestamp": "2026-03-02T12:00:00.000000"
}
```

Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <your-api-token>`
- `X-Api-Key: <your-api-token>`

## Home Screen Shortcut

In Pythonista, open `sns_button.py`, tap the wrench icon, and select "Home Screen".

## Troubleshooting

- "Configuration file not found" - Make sure `.env` is in the same directory as the script
- "Distribution list not found" - Check the CSV path in `.env`
- "Could not connect to server" - Verify the endpoint URL and your internet connection
- "Error: 401/403" - Check your API token
