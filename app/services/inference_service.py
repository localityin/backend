from fastapi import HTTPException
from app.core.config import settings
from pydantic import BaseModel, Field, ValidationError
import httpx
from app.utils.logger import logger

# Define request and response models for the inference endpoint
class InferenceRequest(BaseModel):
    phone: int = Field(..., example=9999999999)
    message: str = Field(..., example="I want to open an account")
    isStore: bool = Field(..., example=True)

class InferenceResponse(BaseModel):
    intent: str
    template_name: str

class InferenceService:
    def __init__(self, base_url=settings.inference_url):
        self.base_url = base_url

    async def get_intent(self, phone: int, message: str, is_store: bool) -> InferenceResponse:
        """
        Calls the /inference endpoint to get the intent and template name.
        """
        inference_url = self.base_url + f"/inference/{'store' if is_store else 'user'}"
        payload = {
            "user_id": str(phone),
            "message": str(message),
            "fast": True
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(inference_url, json=payload, timeout=50.0)
                response.raise_for_status()
                inference_data = response.json()
                return InferenceResponse(**inference_data)
        except httpx.HTTPError as http_err:
            logger.error(f"Inference API HTTP error: {http_err}")
            raise HTTPException(status_code=502, detail="Inference service unavailable")
        except ValidationError as val_err:
            logger.error(f"Inference API response validation error: {val_err}")
            raise HTTPException(status_code=500, detail="Invalid response from inference service")
        except Exception as e:
            logger.error(f"Unexpected error calling inference API: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

# Example usage:
inference_service = InferenceService()
# intent = inference_service.get_intent("Hello", 123, False)
# print(intent)