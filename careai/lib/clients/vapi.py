import os

import requests


def create_vapi_call(customer_number, system_message, first_prompt):
    # Your Vapi API Authorization token
    auth_token = os.environ.get("VAPI_AUTH_TOKEN")
    # The Phone Number ID from the dashboard
    phone_number_id = "63aa98b9-1c7a-4cf5-ab35-0b845d7cc287"

    # Create the header with Authorization token
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    # Create the data payload for the API request
    data = {
        "assistant": {
            "firstMessage": first_prompt,
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": system_message}],
            },
            "voice": "jennifer-playht",
        },
        "phoneNumberId": phone_number_id,
        "customer": {
            "number": customer_number,
        },
    }

    # Make the POST request to Vapi to create the phone call
    response = requests.post(
        "https://api.vapi.ai/call/phone", headers=headers, json=data
    )

    # Check if the request was successful and return the response
    if response.status_code == 201:
        print("Call created successfully")
        return response.json()
    else:
        print("Failed to create call")
        return response.text
