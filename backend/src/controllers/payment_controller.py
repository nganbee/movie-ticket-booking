import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.booking import BookingTable, PaymentTable, ETicketTable, BookingItemTable
from src.models.theater import ShowtimeTable
from src.models.user import UserTable
from src.models.payment import PaymentIntentResponse
from src.services.vnpay_service import VNPayService
from fastapi.responses import RedirectResponse
from src.config.settings import settings

class PaymentController:
    
    @staticmethod
    async def create_intent(db: AsyncSession, user_id: int, booking_id: int, ip_addr: str) -> PaymentIntentResponse:
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
        
        amount = booking.total_price
        order_info = f"Thanh toan ve xem phim cho don hang {booking_id}"
        
        payment_link = VNPayService.generate_payment_url(
            order_id=str(booking_id),
            amount=amount,
            order_info=order_info,
            ip_addr=ip_addr
        )
        
        return PaymentIntentResponse(
            booking_id=booking_id,
            amount=amount,
            qr_url="", # Not used with VNPAY redirect
            payment_link=payment_link
        )
    @staticmethod
    async def process_vnpay_ipn(db: AsyncSession, query_params: dict):
        if not VNPayService.validate_response(query_params.copy()):
            return {"RspCode": "97", "Message": "Invalid Checksum"}
            
        booking_id_str = query_params.get("vnp_TxnRef")
        if not booking_id_str or not booking_id_str.isdigit():
            return {"RspCode": "01", "Message": "Order not found"}
            
        booking_id = int(booking_id_str)
        response_code = query_params.get("vnp_ResponseCode")
        amount = int(query_params.get("vnp_Amount", 0)) // 100
        transaction_no = query_params.get("vnp_TransactionNo")
        
        # Verify booking
        res = await db.execute(select(BookingTable).where(BookingTable.booking_id == booking_id))
        booking = res.scalars().first()
        
        if not booking:
            return {"RspCode": "01", "Message": "Order not found"}
            
        if booking.status == "paid":
            return {"RspCode": "02", "Message": "Order already confirmed"}
            
        if amount != booking.total_price:
            return {"RspCode": "04", "Message": "Invalid amount"}
            
        if response_code == "00":
            # Success
            booking.status = "paid"
            
            # Record payment
            payment = PaymentTable(
                booking_id=booking.booking_id,
                payment_method="VNPAY",
                amount=amount,
                payment_time=datetime.now().astimezone(),
                transaction_id=transaction_no
            )
            db.add(payment)
            
            # Generate ETickets for each booking item and mark seats as Sold
            res_items = await db.execute(select(BookingItemTable).where(BookingItemTable.booking_id == booking.booking_id))
            items = res_items.scalars().all()
            
            from src.models.theater import ShowSeatTable
            
            for item in items:
                # Đổi trạng thái ghế thành Sold
                res_ss = await db.execute(select(ShowSeatTable).where(ShowSeatTable.show_seat_id == item.show_seat_id))
                show_seat = res_ss.scalars().first()
                if show_seat:
                    show_seat.status = "Sold"
                    show_seat.hold_expires_at = None
                    
                eticket = ETicketTable(
                    item_id=item.item_id,
                    qr_code=str(uuid.uuid4()), # Generate a unique ID for the QR
                    issued_at=datetime.now().astimezone(),
                    is_valid=True
                )
                db.add(eticket)
                
            await db.commit()
            return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            # Failed or cancelled
            return {"RspCode": "00", "Message": "Confirm Success (Failed payment)"}

    @staticmethod
    async def process_vnpay_return(db: AsyncSession, query_params: dict):
        if not VNPayService.validate_response(query_params.copy()):
            raise HTTPException(status_code=400, detail="Invalid signature")
            
        response_code = query_params.get("vnp_ResponseCode")
        booking_id_str = query_params.get("vnp_TxnRef")
        
        if response_code == "24":
            # User cancelled, we should call booking_controller to release seats
            from src.controllers.booking_controller import BookingController
            if booking_id_str and booking_id_str.isdigit():
                await BookingController.cancel_booking(db, int(booking_id_str))
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/profile")
                
        # Redirect back to frontend receipt page on success
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/receipt/{booking_id_str}")
