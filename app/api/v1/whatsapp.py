# app/routers/whatsapp_webhook.py

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Dict, List, Optional
from app.core.database import db
import httpx
import logging

from app.core.config import settings

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the schema for WhatsApp webhook payload
class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

# Define request and response models for the inference endpoint
class InferenceRequest(BaseModel):
    phone: int = Field(..., example=9999999999)
    message: str = Field(..., example="I want to open an account")
    isStore: bool = Field(..., example=True)

class InferenceResponse(BaseModel):
    intent: str
    template_name: str

# Define the function to extract message data from payload
def extract_message_data(payload: WhatsAppWebhookPayload) -> Optional[Dict[str, Any]]:
    """
    Extracts phone number and message from the webhook payload.
    """
    try:
        for entry in payload.entry:
            changes = entry.get("changes", [])
            for change in changes:
                if change.get("field") == "messages":
                    messages = change["value"].get("messages", [])
                    for message in messages:
                        if message.get("type") == "text":
                            phone_number = message.get("from")
                            message_body = message["text"].get("body")
                            if phone_number and message_body:
                                return {
                                    "phone": int(phone_number),
                                    "message": message_body
                                }
        return None
    except Exception as e:
        logger.error(f"Error extracting message data: {e}")
        return None

# Define the function to call the inference endpoint
async def call_inference(phone: int, message: str, is_store: bool) -> InferenceResponse:
    """
    Calls the /inference endpoint to get the intent and template name.
    """
    inference_url = settings.inference_url + '/inference'
    payload = {
        "phone": phone,
        "message": message,
        "isStore": is_store
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(inference_url, json=payload, timeout=10.0)
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

# Define the function to fetch the template from MongoDB
async def fetch_template(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the template document from the 'templates' collection based on template_name.
    """
    try:
        template = await db.templates.find_one({"template_name": template_name})
        if not template:
            logger.error(f"Template '{template_name}' not found in the database.")
            return None
        return template
    except Exception as e:
        logger.error(f"Error fetching template from DB: {e}")
        return None


async def fetch_data_points(intent: str, phone: int, is_store: bool) -> Dict[str, Any]:
    """
    Fetches the necessary data points from MongoDB collections based on the intent and template requirements.
    
    Parameters:
    - intent (str): The inferred intent from the inference server.
    - phone (int): The phone number of the user or store.
    - is_store (bool): Flag indicating if the message is from a store.
    
    Returns:
    - Dict[str, Any]: A dictionary containing the required data points for the template.
    """
    data_points = {}
    try:
        if is_store:
            # Handle Store Intents
            if intent in ["store_welcome_onboarding", "store_gstin_onboarding", "store_location_onboarding"]:
                # No additional data required
                logger.info(f"No data points required for intent '{intent}' from store.")
                pass  # No data to fetch
            
            elif intent == "store_onboarding_complete":
                # Static or predefined data points
                data_points['inventory_link'] = f"{settings.base_url}/store/{phone}/inventory"  # Example link
                logger.info("Fetched inventory link for 'store_onboarding_complete' intent.")
            
            elif intent == "store_order_request":
                # Fetch the latest pending order for the store
                order = await db.orders.find_one(
                    {"storeId": f"str_{phone}", "status": "pending"},
                    sort=[("createdAt", -1)]
                )
                if order:
                    # Fetch product details for each SKU
                    items = []
                    for item in order.get("items", []):
                        product = await db.products.find_one({"_id": item["productId"]})
                        if product:
                            items.append({
                                "product_name": product.get("name", "Product"),
                                "sku_name": next((sku["name"] for sku in product.get("skus", []) if sku["_id"] == item["skuId"]), "SKU"),
                                "quantity": item.get("quantity", 0),
                                "price": float(item.get("price", 0.0))
                            })
                    data_points['order_items'] = items
                    data_points['order_total_amount'] = float(order.get("total", 0.0))
                    logger.info(f"Fetched order details for 'store_order_request' intent: Order ID {order.get('_id')}")
                else:
                    data_points['order_items'] = []
                    data_points['order_total_amount'] = 0.0
                    logger.warning(f"No pending orders found for store with phone {phone} for 'store_order_request' intent.")
            
            elif intent == "store_unknown_message":
                # Provide links and buttons as per the template
                data_points['inventory_link'] = f"{settings.base_url}/store/{phone}/inventory"
                data_points['todays_revenue_button'] = "Get Today's Revenue"
                data_points['close_store_button'] = "Close Store for Today"
                logger.info("Fetched data points for 'store_unknown_message' intent.")
            
            elif intent == "store_daily_revenue":
                # Fetch today's revenue from analytics
                from datetime import datetime, timedelta
                
                today = datetime.utcnow().date()
                start_date = datetime.combine(today, datetime.min.time())
                end_date = datetime.combine(today, datetime.max.time())
                
                analytics = await db.analytics.find_one({
                    "storeId": f"str_{phone}",
                    "startDate": {"$lte": start_date},
                    "endDate": {"$gte": end_date}
                })
                if analytics:
                    data_points['todays_revenue_amount'] = float(analytics['metrics'].get('totalRevenue', 0.0))
                    data_points['store_name'] = await get_store_name(phone)
                    logger.info(f"Fetched analytics for 'store_daily_revenue' intent: Revenue {data_points['todays_revenue_amount']}")
                else:
                    data_points['todays_revenue_amount'] = 0.0
                    data_points['store_name'] = await get_store_name(phone)
                    logger.warning(f"No analytics data found for store with phone {phone} for 'store_daily_revenue' intent.")
            
            elif intent == "store_toggle_status":
                # Provide action buttons
                data_points['open_store_button'] = "Open Store"
                logger.info("Fetched data points for 'store_toggle_status' intent.")
            
            else:
                logger.warning(f"Unhandled store intent: {intent}")
        
        else:
            # Handle User Intents
            if intent == "user_welcome_onboarding":
                # Fetch user's name
                user = await db.users.find_one({"phone": str(phone)})
                if user:
                    data_points['user_name'] = user.get("name", "User")
                    logger.info(f"Fetched user name for 'user_welcome_onboarding' intent: {data_points['user_name']}")
                else:
                    data_points['user_name'] = "User"
                    logger.warning(f"No user found with phone {phone} for 'user_welcome_onboarding' intent.")
            
            elif intent == "user_delivery_location":
                # No additional data required
                logger.info(f"No data points required for intent '{intent}' from user.")
                pass  # No data to fetch
            
            elif intent == "user_order_init":
                # Fetch user's name
                user = await db.users.find_one({"phone": str(phone)})
                if user:
                    data_points['user_name'] = user.get("name", "User")
                    logger.info(f"Fetched user name for 'user_order_init' intent: {data_points['user_name']}")
                else:
                    data_points['user_name'] = "User"
                    logger.warning(f"No user found with phone {phone} for 'user_order_init' intent.")
            
            elif intent == "user_confirm_cart":
                # Fetch the latest accepted or pending order for the user
                order = await db.orders.find_one(
                    {"userId": f"usr_{phone}", "status": {"$in": ["pending", "accepted"]}},
                    sort=[("createdAt", -1)]
                )
                if order:
                    # Fetch product and SKU details
                    cart_items = []
                    for item in order.get("items", []):
                        product = await db.products.find_one({"_id": item["productId"]})
                        if product:
                            sku = next((sku for sku in product.get("skus", []) if sku["_id"] == item["skuId"]), None)
                            if sku:
                                cart_items.append({
                                    "product_name": product.get("name", "Product"),
                                    "sku_name": sku.get("name", "SKU"),
                                    "quantity": item.get("quantity", 0),
                                    "price": float(item.get("price", 0.0))
                                })
                    data_points['cart_items_list'] = cart_items
                    data_points['cart_total'] = float(order.get("total", 0.0))
                    logger.info(f"Fetched cart details for 'user_confirm_cart' intent: Order ID {order.get('_id')}")
                else:
                    data_points['cart_items_list'] = []
                    data_points['cart_total'] = 0.0
                    logger.warning(f"No active cart found for user with phone {phone} for 'user_confirm_cart' intent.")
            
            elif intent == "user_order_delivery_estimate":
                # Fetch the latest delivered order to provide an estimated delivery time
                # This is a placeholder; implement actual logic as needed
                data_points['estimated_delivery_time'] = "30 minutes"
                logger.info(f"Set estimated delivery time for 'user_order_delivery_estimate' intent.")
            
            elif intent == "user_rate_order":
                # Requires order_id, delivery time, store name
                # Assume order_id is passed in the message or context; here, we'll fetch the latest delivered order
                order = await db.orders.find_one(
                    {"userId": f"usr_{phone}", "status": "delivered"},
                    sort=[("updatedAt", -1)]
                )
                if order:
                    data_points['order_id'] = order.get("_id", "")
                    data_points['delivery_time'] = order.get("updatedAt").isoformat() if order.get("updatedAt") else ""
                    store = await db.stores.find_one({"_id": order.get("storeId")})
                    data_points['store_name'] = store.get("name", "Store") if store else "Store"
                    data_points['rating_link'] = f"{settings.base_url}/rate_order/{order.get('_id')}"
                    logger.info(f"Fetched order details for 'user_rate_order' intent: Order ID {order.get('_id')}")
                else:
                    data_points['order_id'] = ""
                    data_points['delivery_time'] = ""
                    data_points['store_name'] = "Store"
                    data_points['rating_link'] = ""
                    logger.warning(f"No delivered orders found for user with phone {phone} for 'user_rate_order' intent.")
            
            elif intent == "user_cart_discarded":
                # No additional data required
                logger.info(f"No data points required for intent '{intent}' from user.")
                pass  # No data to fetch
            
            elif intent == "user_order_status":
                # Requires order_id and store name
                # Assume order_id is passed in the message or context; here, we'll fetch the latest order
                order = await db.orders.find_one(
                    {"userId": f"usr_{phone}"},
                    sort=[("updatedAt", -1)]
                )
                if order:
                    data_points['order_id'] = order.get("_id", "")
                    data_points['order_status'] = order.get("status", "Unknown")
                    store = await db.stores.find_one({"_id": order.get("storeId")})
                    data_points['store_name'] = store.get("name", "Store") if store else "Store"
                    logger.info(f"Fetched order details for 'user_order_status' intent: Order ID {order.get('_id')}")
                else:
                    data_points['order_id'] = ""
                    data_points['order_status'] = "No orders found"
                    data_points['store_name'] = "Store"
                    logger.warning(f"No orders found for user with phone {phone} for 'user_order_status' intent.")
            
            elif intent in ["user_unknown_message", "user_no_order"]:
                # No additional data required
                logger.info(f"No data points required for intent '{intent}' from user.")
                pass  # No data to fetch
            
            else:
                logger.warning(f"Unhandled user intent: {intent}")
        
        return data_points
    except Exception as e:
        logger.error(f"Error fetching data points: {e}")
        return data_points  # Return whatever data has been fetched so far
    
async def get_store_name(phone: int) -> str:
    """
    Helper function to fetch the store's name based on the phone number.
    """
    store = await db.stores.find_one({"phone": str(phone)})
    if store:
        return store.get("name", "Store")
    else:
        return "Store"
        
# Define the function to send message via WhatsApp service
async def send_whatsapp_message(template_id: str, data_points: Dict[str, Any], phone_number: int):
    """
    Sends a message to the user or store via the WhatsApp API using the specified template and data points.
    """
    try:
        whatsapp_api_url = 'https://api.whatsapp.com/send'
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_secret}", # replace this with user app specifici token
            "Content-Type": "application/json"
        }
        payload = {
            "template_id": template_id,
            "to": str(phone_number),
            "data": data_points,
            # Include other required fields as per WhatsApp API documentation
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(whatsapp_api_url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Message sent to {phone_number} via WhatsApp.")
    except httpx.HTTPError as http_err:
        logger.error(f"WhatsApp API HTTP error: {http_err}")
    except Exception as e:
        logger.error(f"Unexpected error sending WhatsApp message: {e}")

# Define a common processing function
async def process_message(phone: int, message: str, is_store: bool):
    """
    Orchestrates the processing of an incoming message: inference, template fetching, data fetching, and message sending.
    """
    try:
        # Step 1: Call inference to get intent and template_name
        inference_response = await call_inference(phone, message, is_store)
        intent = inference_response.intent
        template_name = inference_response.template_name

        logger.info(f"Inferred intent: {intent}, Template: {template_name} for phone: {phone}")

        # Step 2: Fetch the corresponding template from MongoDB
        template = await fetch_template(template_name)
        if not template:
            logger.error(f"Template '{template_name}' not found. Aborting message sending.")
            return

        template_id = template.get("template_id")
        if not template_id:
            logger.error(f"Template ID missing for template '{template_name}'. Aborting message sending.")
            return

        # Step 3: Fetch required data points based on the template's data fields
        data_fields = template.get("data", [])
        data_points = await fetch_data_points(intent, phone, is_store)

        # Optional: Validate that all required data points are present
        missing_fields = [field for field in data_fields if field not in data_points]
        if missing_fields:
            logger.warning(f"Missing data points for template '{template_name}': {missing_fields}")
            # You can decide to handle this case differently, e.g., send a default message or skip
            # For now, we'll proceed with available data points

        # Step 4: Send the message via WhatsApp service
        await send_whatsapp_message(template_id, data_points, phone)

    except HTTPException as http_exc:
        logger.error(f"HTTPException during message processing: {http_exc.detail}")
    except Exception as e:
        logger.error(f"Unexpected error during message processing: {e}")

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

# Define the POST webhook handler for user
@router.post("/webhook")
async def user_webhook(payload: WhatsAppWebhookPayload, background_tasks: BackgroundTasks):
    """
    Handles incoming WhatsApp webhook messages from users.
    """
    logger.info("payload: ", payload)
    logger.info("Received webhook payload.")
    # Extract message data
    message_data = extract_message_data(payload, is_store=False)
    if not message_data:
        logger.warning("No valid message data found in user webhook payload.")
        return {"message": "No valid message data found."}

    phone = message_data["phone"]
    message = message_data["message"]

    logger.info(f"Processing message from phone: {phone}, message: {message}")

    # Add the message processing task to background tasks
    # background_tasks.add_task(process_message, phone, message, is_store)

    return {"message": "Whatsapp webhook received and is being processed."}