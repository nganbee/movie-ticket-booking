from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.controllers.payment_controller import PaymentController
from src.models.payment import PaymentIntentResponse, WebhookPayload
from src.middlewares.auth import get_current_user
from src.models.user import UserTable

router = APIRouter()

@router.post("/create-intent/{booking_id}", response_model=PaymentIntentResponse)
async def create_intent(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    return await PaymentController.create_intent(db, current_user.user_id, booking_id)

@router.post("/webhook")
async def process_webhook(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    # Note: In real life, webhook doesn't have current_user.
    # It relies on Signature verification to authenticate the gateway.
    return await PaymentController.process_webhook(db, payload)
