import openai
import logging
from typing import List, Dict, Union
from app.core.config import settings

logger = logging.getLogger("inference_service")

class InferenceService:
    def __init__(self, api_key: str):
        """
        Initialize the Inference Service with the OpenAI API key.
        """
        openai.api_key = api_key

    async def infer_intent(self, message: str) -> str:
        """
        Infer the intent of a user's message.

        Args:
            message (str): The user's message.

        Returns:
            str: The inferred intent (e.g., 'onboarding', 'order', 'location', 'inventory', 'unknown').
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a WhatsApp assistant for Locality, a grocery store platform. "
                        "Identify the intent behind the user's message. Possible intents are: "
                        "'onboarding', 'order', 'location', 'inventory', 'unknown'."
                    )
                },
                {
                    "role": "user",
                    "content": f"Message: '{message}'."
                }
            ]

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=20,
                temperature=0
            )
            intent = response["choices"][0]["message"]["content"].strip().lower()
            logger.info(f"Inferred intent: {intent}")
            return intent
        except Exception as e:
            logger.error(f"Error inferring intent: {e}")
            return "unknown"

    async def parse_order(self, message: str) -> List[Dict[str, Union[str, int]]]:
        """
        Parse a user's order message into structured items.

        Args:
            message (str): The user's order message.

        Returns:
            List[Dict[str, Union[str, int]]]: A list of parsed order items, each containing:
                - item_name (str): The name of the item.
                - quantity (int): The quantity of the item.
                - unit (str): The unit of measurement.
        """
        try:
            parse_prompt = (
                "You are an assistant that extracts order details from user messages. Parse the user's message into "
                "a JSON array where each item has:\n"
                "- item_name: Name of the item.\n"
                "- quantity: Quantity of the item (numeric).\n"
                "- unit: Unit of measurement (e.g., kg, liter, packets).\n\n"
                "If the unit is not provided, return 'units' as the default. Ensure all quantities are numeric.\n\n"
                f"Message: '{message}'"
            )

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": parse_prompt}],
                max_tokens=200,
                temperature=0
            )
            order_items = eval(response["choices"][0]["message"]["content"])  # Parse the JSON response
            logger.info(f"Parsed order items: {order_items}")
            return order_items
        except Exception as e:
            logger.error(f"Error parsing order: {e}")
            return []
        
inference_service = InferenceService(api_key=settings.openai_api_key)