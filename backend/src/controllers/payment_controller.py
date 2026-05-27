import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.booking import BookingTable, PaymentTable, ETicketTable, BookingItemTable
from src.models.theater import ShowtimeTable
from src.models.user import UserTable
from src.models.payment import PaymentIntentResponse, WebhookPayload

class PaymentController:
    
    @staticmethod
    async def create_intent(db: AsyncSession, user_id: int, booking_id: int) -> PaymentIntentResponse:
        # Check if booking exists and belongs to user
        res = await db.execute(select(BookingTable).where(
            BookingTable.booking_id == booking_id,
            BookingTable.customer_id == user_id
        ))
        booking = res.scalars().first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status != "pending":
            raise HTTPException(status_code=400, detail=f"Booking is already {booking.status}")
        
        # Generate VietQR link (Mock VietQR format)
        # format: https://img.vietqr.io/image/<BANK_BIN>-<ACCOUNT_NO>-compact2.png?amount=<AMOUNT>&addInfo=<INFO>
        bank_bin = "970436" # Vietcombank
        account_no = "0123456789"
        add_info = f"ThanhToanBK{booking_id}"
        amount = booking.total_price
        
        qr_url = f"https://img.vietqr.io/image/{bank_bin}-{account_no}-compact2.png?amount={amount}&addInfo={add_info}&accountName=CINEBOOK"
        payment_link = f"https://payment.cinebook.vn/pay/{booking_id}"
        
        return PaymentIntentResponse(
            booking_id=booking_id,
            amount=amount,
            qr_url=qr_url,
            payment_link=payment_link
        )

    @staticmethod
    async def process_webhook(db: AsyncSession, payload: WebhookPayload):
        if payload.status != "success":
            return {"status": "ignored", "message": "Status is not success"}
            
        # Verify booking
        res = await db.execute(select(BookingTable).where(BookingTable.booking_id == payload.booking_id))
        booking = res.scalars().first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        if booking.status == "paid":
            return {"status": "success", "message": "Already paid"}
            
        if payload.amount < booking.total_price:
            raise HTTPException(status_code=400, detail="Insufficient amount")
            
        # Update booking status
        booking.status = "paid"
        
        # Record payment
        payment = PaymentTable(
            booking_id=booking.booking_id,
            payment_method="Bank Transfer",
            amount=payload.amount,
            payment_time=datetime.now().astimezone(),
            transaction_id=payload.transaction_id
        )
        db.add(payment)
        
        # Generate ETickets for each booking item
        res_items = await db.execute(select(BookingItemTable).where(BookingItemTable.booking_id == booking.booking_id))
        items = res_items.scalars().all()
        
        for item in items:
            eticket = ETicketTable(
                item_id=item.item_id,
                qr_code=str(uuid.uuid4()), # Generate a unique ID for the QR
                issued_at=datetime.now().astimezone(),
                is_valid=True
            )
            db.add(eticket)
            
        await db.commit()
        return {"status": "success", "message": "Payment processed and tickets issued"}
