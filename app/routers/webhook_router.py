from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from app.services import user_service, order_service, store_service
import json
from app.services.conversation_service import ConversationService
from app.config import settings

router = APIRouter()
conversation_service = ConversationService()


@router.get("/webhook/user")
async def verify_webhook_user(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.secret:
        return int(hub_challenge)
    else:
        raise HTTPException(
            status_code=403, detail="Verification token mismatch")


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


@router.get("/webhook/store")
async def verify_webhook_store(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.secret:
        return int(hub_challenge)
    else:
        raise HTTPException(
            status_code=403, detail="Verification token mismatch")


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
