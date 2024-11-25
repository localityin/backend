# app/routers/whatsapp_webhook.py

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.utils.logger import logger
from app.utils.datetime import get_ist_time

from app.core.config import settings
from app.core.database import db
from app.core.config import settings

from app.services.inference_service import inference_service
from app.services.openai_service import inference_service
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()

# Define the schema for WhatsApp webhook payload
class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

# Define the function to extract message data from payload
def extract_message_data(payload: WhatsAppWebhookPayload) -> Optional[Dict[str, Any]]:
    """
    Extracts phone number and message/location data from the webhook payload.
    """
    try:
        for entry in payload.entry:
            changes = entry.get("changes", [])
            for change in changes:
                if change.get("field") == "messages":
                    messages = change["value"].get("messages", [])
                    for message in messages:
                        phone_number = message.get("from")
                        
                        # Handle text messages
                        if message.get("type") == "text":
                            message_body = message["text"].get("body")
                            if phone_number and message_body:
                                return {
                                    "phone": int(phone_number),
                                    "message_type": "text",
                                    "message": message_body
                                }

                        # Handle location messages
                        if message.get("type") == "location":
                            location = message["location"]
                            if phone_number and location:
                                return {
                                    "phone": int(phone_number),
                                    "message_type": "location",
                                    "location": {
                                        "latitude": location["latitude"],
                                        "longitude": location["longitude"],
                                        "name": location.get("name", ""),
                                        "address": location.get("address", "")
                                    }
                                }
        return None
    except Exception as e:
        logger.error(f"Error extracting message data: {e}")
        return None

async def process_message(phone: int, message: Optional[str], is_store: bool, message_type: str = "text", location: Optional[dict] = None):
    """
    Processes an incoming WhatsApp message or location, handles conversational flow, database interactions,
    and sends appropriate responses using WhatsApp templates.
    """
    try:
        # Identify the database collection based on user/store
        collection = db.stores if is_store else db.users
        entity = await collection.find_one({"phone": phone})

        # If user/store does not exist, initiate onboarding
        if not entity:
            logger.info(f"New {'store' if is_store else 'user'} detected. Starting onboarding.")
            template_id = "store_onboarding" if is_store else "user_onboarding"
            placeholders = ["Friend"]  # Placeholder for user/store greeting
            await collection.insert_one({
                "phone": phone,
                "state": "onboarding",
                "created_at": get_ist_time(),
                "updated_at": get_ist_time()
            })
            await whatsapp_service.send_message(template_id, placeholders, phone, is_store)
            return

        # Get the current state of the user/store
        state = entity.get("state", "default")
        logger.info(f"Current state for {phone}: {state}")

        # Handle location messages
        if message_type == "location" and location:
            # Save the location in the database
            await collection.update_one(
                {"phone": phone},
                {
                    "$set": {
                        "location": {
                            "latitude": location["latitude"],
                            "longitude": location["longitude"],
                            "name": location.get("name", ""),
                            "address": location.get("address", "")
                        },
                        "state": "default",
                        "updated_at": get_ist_time()
                    }
                }
            )

            # Respond to the user with a confirmation
            response_message = f"Thank you for sharing your location: {location.get('name', 'Unknown')}, {location.get('address', 'No address provided')}."
            await whatsapp_service.send_message("location_update", [response_message], phone, is_store)
            return

        # Step 1: Use OpenAI to infer intent if it's a text message
        if message_type == "text" and message:
            intent = await inference_service.infer_intent(message)

            # Step 2: Handle intents
            if state == "onboarding":
                # Handle onboarding flow
                if "name" in message.lower():
                    field = "store_name" if is_store else "name"
                    await collection.update_one(
                        {"phone": phone},
                        {"$set": {field: message, "state": "default", "updated_at": get_ist_time()}}
                    )
                    response = "Thank you! Your account is set up. How can we assist you today?"
                    await whatsapp_service.send_message("user_onboarding_complete", [response], phone, is_store)
                    return
                else:
                    response = "Please provide your name to complete the onboarding process."
                    await whatsapp_service.send_message("user_onboarding", [response], phone, is_store)
                    return

            elif intent == "order":
                if state != "awaiting_order":
                    await collection.update_one({"phone": phone}, {"$set": {"state": "awaiting_order", "updated_at": get_ist_time()}})
                    await whatsapp_service.send_message("order_prompt", [], phone, is_store)
                    return
                else:
                    order_items = await inference_service.parse_order(message)

                    # Process the order and save to the database
                    try:
                        total_price = sum(item["quantity"] * 100 for item in order_items)  # Example pricing logic
                        order_id = await db.orders.insert_one({
                            "user_id": entity["_id"],
                            "items": order_items,
                            "total_price": total_price,
                            "status": "pending",
                            "created_at": get_ist_time(),
                            "updated_at": get_ist_time()
                        }).inserted_id

                        # Update state and send confirmation
                        await collection.update_one({"phone": phone}, {"$set": {"state": "default", "updated_at": get_ist_time()}})
                        await whatsapp_service.send_message("order_confirmation", [str(order_id), str(total_price)], phone, is_store)
                    except Exception as e:
                        logger.error(f"Error processing order for {phone}: {e}")
                        await whatsapp_service.send_message("default_error", ["An error occurred while processing your order."], phone, is_store)
                    return


            elif intent == "location":
                # Save the location as text
                await collection.update_one(
                    {"phone": phone},
                    {"$set": {"location_text": message, "state": "default", "updated_at": get_ist_time()}}
                )
                await whatsapp_service.send_message("location_update", [message], phone, is_store)
                return

            elif intent == "inventory" and is_store:
                # Prompt store to update inventory
                await whatsapp_service.send_message("inventory_update_prompt", [], phone, is_store)
                return

            # Handle unknown intents
            await whatsapp_service.send_message("unknown_intent", ["I'm sorry, I didn't understand that."], phone, is_store)

    except Exception as e:
        logger.error(f"Error processing message for {phone}: {e}")
        await whatsapp_service.send_message("default_error", ["An unexpected error occurred."], phone, is_store)

# Define the GET webhook verification for user
@router.get("/webhook")
async def verify_webhook_user(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Verifies the WhatsApp webhook for user endpoints.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_secret:
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")

def get_phone_number(payload: WhatsAppWebhookPayload):
    """
    Extracts phone number from the webhook payload.
    """
    try:
        for entry in payload.entry:
            changes = entry.get("changes", [])
            for change in changes:
                if change.get("field") == "messages":
                    message_metadata = change["value"].get("metadata", {})
                    if message_metadata:
                        phone_number = message_metadata.get("display_phone_number")
                        if phone_number:
                            return phone_number
        return None
    except Exception as e:
        logger.error(f"Error extracting phone number: {e}")

# Define the POST webhook handler for user
@router.post("/webhook")
async def user_webhook(payload: WhatsAppWebhookPayload, background_tasks: BackgroundTasks):
    """
    Handles incoming WhatsApp webhook messages from users.
    """
    logger.info("Received webhook payload.")
    # Extract message data

    recieving_number = get_phone_number(payload)
    if not recieving_number:
        logger.warning("No valid phone number found in user webhook payload.")
        return {"message": "No valid phone number found."}
    
    is_store = None
    if recieving_number == settings.whatsapp_store_number:
        is_store = True
    elif recieving_number == settings.whatsapp_user_number:
        is_store = False
    else:
        logger.warning("No valid phone number found in user webhook payload.")
        return {"message": "No valid phone number found."}
    
    message_data = extract_message_data(payload)
    if not message_data:
        logger.warning("No valid message data found in user webhook payload.")
        return {"message": "No valid message data found."}

    phone = message_data["phone"]
    message_type = message_data.get("message_type", "text")
    message = message_data.get("message", "")
    location = message_data.get("location", None)

    logger.info(f"Processing message from phone: {phone}, type: {message_type}, message: {message}, location: {location}")

    # Add the message processing task to background tasks
    background_tasks.add_task(process_message, phone, message, False, message_type, location)

    return {"message": "Whatsapp webhook received and is being processed."}