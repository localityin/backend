import httpx
import logging
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger("whatsapp_service")


class WhatsAppService:
    def __init__(self, user_number_id: str, store_number_id: str, token: str):
        """
        Initialize the WhatsApp Service with API credentials.

        Args:
            user_number_id (str): WhatsApp Business ID for user interactions.
            store_number_id (str): WhatsApp Business ID for store interactions.
            token (str): WhatsApp API access token.
        """
        self.user_number_id = user_number_id
        self.store_number_id = store_number_id
        self.token = token

    async def send_message(self, phone_number: int, template_id: str, placeholders: List[str], is_store: bool = False):
        """
        Sends a WhatsApp template message to the user or store.

        Args:
            phone_number (int): The recipient's phone number.
            template_id (str): The template name approved by WhatsApp.
            placeholders (List[str]): List of placeholder values for the template.
            is_store (bool): Whether the message is for a store or user (default: False).

        Returns:
            dict: The response from the WhatsApp Business API.
        """
        try:
            # Determine the WhatsApp Business ID
            whatsapp_phone_id = self.store_number_id if is_store else self.user_number_id
            api_url = f"https://graph.facebook.com/v15.0/{whatsapp_phone_id}/messages"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            # Build the template message payload
            components = [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": placeholder} for placeholder in placeholders]
                }
            ]

            payload = {
                "messaging_product": "whatsapp",
                "to": str(phone_number),
                "type": "template",
                "template": {
                    "name": template_id,
                    "language": {"code": "en"},
                    "components": components
                }
            }

            async with httpx.AsyncClient() as client:
                logger.info(f"Sending WhatsApp message to {phone_number} using template '{template_id}'.")
                response = await client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"WhatsApp message sent successfully: {response.json()}")
                return response.json()

        except httpx.RequestError as e:
            logger.error(f"Request error while sending WhatsApp message to {phone_number}: {e}")
            return {"error": "Request error", "details": str(e)}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while sending WhatsApp message to {phone_number}: {e.response.text}")
            return {"error": "HTTP error", "details": e.response.text}
        except Exception as e:
            logger.error(f"Unexpected error while sending WhatsApp message to {phone_number}: {e}")
            return {"error": "Unexpected error", "details": str(e)}
        

whatsapp_service = WhatsAppService(
    user_number_id=settings.whatsapp_user_number_id,
    store_number_id=settings.whatsapp_store_number_id,
    token=settings.whatsapp_token
)