import requests


def send_whatsapp_message(access_token: str, receiver_number: str, template_id: str, template_variables: dict):
    url = f"https://graph.facebook.com/v13.0/{receiver_number}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": receiver_number,
        "type": "template",
        "template": {
            "name": template_id,
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": value}
                        for value in template_variables.values()
                    ]
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
