from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.models.payment import PaymentCreate, PaymentResponse
from app.core.razorpay_client import razorpay_client
from app.utils.security import get_current_user, get_current_store
from app.core.database import db
from nanoid import generate
import razorpay
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.post("/create-order", response_model=PaymentResponse)
async def create_payment_order(payment: PaymentCreate, current_user: dict = Depends(get_current_user)):
    payment_id = f"pay_{generate(size=10)}"
    
    # Create Razorpay Order
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": int(payment.amount * 100),  # Convert to paise
            "currency": payment.currency,
            "receipt": payment_id,
            "payment_capture": 1
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    payment_data = payment.dict()
    payment_data.update({
        "_id": payment_id,
        "razorpay_order_id": razorpay_order['id'],
        "status": "created",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db["payments"].insert_one(payment_data)
    return PaymentResponse(**payment_data)

@router.post("/verify")
async def verify_payment(order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    payment = await db["payments"].find_one({"razorpay_order_id": order_id})
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment order not found")
    
    try:
        # Verify payment signature with Razorpay
        params = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        razorpay_client.utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError:
        await db["payments"].update_one({"razorpay_order_id": order_id}, {"$set": {"status": "failed"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment verification failed")
    
    # Update payment status to captured in MongoDB
    await db["payments"].update_one(
        {"razorpay_order_id": order_id},
        {"$set": {"status": "captured", "razorpay_payment_id": razorpay_payment_id, "updated_at": datetime.utcnow()}}
    )
    updated_payment = await db["payments"].find_one({"razorpay_order_id": order_id})
    return PaymentResponse(**updated_payment)

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    # Verify the webhook signature
    body = await request.body()
    signature = request.headers.get('X-Razorpay-Signature')
    try:
        razorpay_client.utility.verify_webhook_signature(body, signature, settings.razorpay_api_secret)
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event")
    order_id = payload["payload"]["payment"]["entity"]["order_id"]
    payment_status = "captured" if event == "payment.captured" else "failed"

    # Update payment status in MongoDB
    await db["payments"].update_one(
        {"razorpay_order_id": order_id},
        {"$set": {"status": payment_status, "updated_at": datetime.utcnow()}}
    )

    return {"status": "success"}

@router.get("/status/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(payment_id: str, current_user: dict = Depends(get_current_user)):
    payment = await db["payments"].find_one({"_id": payment_id, "user_id": current_user["_id"]})
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentResponse(**payment)
