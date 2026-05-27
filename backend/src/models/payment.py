from pydantic import BaseModel
from typing import Optional

class PaymentIntentResponse(BaseModel):
    booking_id: int
    amount: int
    qr_url: str
    payment_link: str

class WebhookPayload(BaseModel):
    transaction_id: str
    booking_id: int
    amount: int
    status: str # "success" or "failed"
    signature: str # Mock signature to verify
