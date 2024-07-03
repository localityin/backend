from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.services import user_service, order_service, store_service
import json
from app.services.conversation_service import ConversationService

router = APIRouter()
conversation_service = ConversationService()


class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: list


@router.post("/webhook/user")
async def user_webhook(payload: WhatsAppWebhookPayload):
    print('user webhook: ', payload.model_dump_json())
    # for entry in payload.entry:
    #     for change in entry.get("changes", []):
    #         if change["field"] == "messages":
    #             message_data = change["value"]["messages"][0]
    #             mobile_number = message_data["from"]
    #             message = message_data["text"]["body"]
    #             response = conversation_service.conversation_engine(
    #                 mobile_number, message)
    #             print('User webhook response: ', response)
    return {"message": "User webhook received"}


@router.post("/webhook/store")
async def store_webhook(payload: WhatsAppWebhookPayload):
    # Process store messages from WhatsApp webhook
    # for entry in payload.entry:
    #     for change in entry.get("changes", []):
    #         value = change.get("value")
    #         if value and value.get("messages"):
    #             for message in value["messages"]:
    #                 # Extract relevant data from the message
    #                 store_id = message["from"]
    #                 message_text = message["text"]["body"]
    #                 # Process the message (e.g., confirm order, update status)
    #                 await store_service.process_message(store_id, message_text)
    print('Store webhook payload: ', json.dumps(payload))
    return {"message": "Store webhook received"}
