import razorpay
from app.core.config import settings

razorpay_client = razorpay.Client(auth=(settings.razorpay_api_key, settings.razorpay_api_secret))
