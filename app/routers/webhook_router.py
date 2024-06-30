from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.services import user_service, order_service, store_service

router = APIRouter()


class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: list


@router.post("/webhook/user")
async def user_webhook(payload: WhatsAppWebhookPayload):
    # Process user messages from WhatsApp webhook
    for entry in payload.entry:
        for change in entry.get("changes", []):
            value = change.get("value")
            if value and value.get("messages"):
                for message in value["messages"]:
                    # Extract relevant data from the message
                    user_id = message["from"]
                    message_text = message["text"]["body"]
                    # Process the message (e.g., place order, check status)
                    await user_service.process_message(user_id, message_text)
    return {"message": "User webhook received"}


@router.post("/webhook/store")
async def store_webhook(payload: WhatsAppWebhookPayload):
    # Process store messages from WhatsApp webhook
    for entry in payload.entry:
        for change in entry.get("changes", []):
            value = change.get("value")
            if value and value.get("messages"):
                for message in value["messages"]:
                    # Extract relevant data from the message
                    store_id = message["from"]
                    message_text = message["text"]["body"]
                    # Process the message (e.g., confirm order, update status)
                    await store_service.process_message(store_id, message_text)
    return {"message": "Store webhook received"}
