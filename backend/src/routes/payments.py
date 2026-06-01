from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.controllers.payment_controller import PaymentController
from src.models.payment import PaymentIntentResponse
from src.middlewares.auth import get_current_user
from src.models.user import UserTable

router = APIRouter()

@router.post("/create-intent/{booking_id}", response_model=PaymentIntentResponse)
async def create_intent(
    booking_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    ip_addr = request.client.host
    return await PaymentController.create_intent(db, current_user.user_id, booking_id, ip_addr)

@router.get("/vnpay-ipn")
async def process_vnpay_ipn(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # VNPAY IPN calls this URL with query params
    query_params = dict(request.query_params)
    return await PaymentController.process_vnpay_ipn(db, query_params)

@router.get("/vnpay-return")
async def process_vnpay_return(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Frontend redirect handler
    query_params = dict(request.query_params)
    return await PaymentController.process_vnpay_return(db, query_params)
