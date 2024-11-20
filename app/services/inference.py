import requests
from app.core.config import settings

class InferenceService:
    def __init__(self, base_url=settings.inference_url):
        self.base_url = base_url

    def get_intent(self, message, user_id, is_store):
        endpoint = f"{self.base_url}/inference/{"store" if is_store else "user"}"

        payload = {
            "message": message,
            "user_id": user_id,
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("intent")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
# inference_service = InferenceService()
# intent = inference_service.get_intent("Hello", 123, False)
# print(intent)