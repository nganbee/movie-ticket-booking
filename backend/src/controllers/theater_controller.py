from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from src.models.theater import TheaterTable, RoomTable

class TheaterController:
    @staticmethod
    async def create_theater(db: AsyncSession, name: str, address: str):
        new_theater = TheaterTable(name=name, address=address)
        db.add(new_theater)
        await db.commit()
        await db.refresh(new_theater)
        return new_theater

    @staticmethod
    async def update_theater(db: AsyncSession, theater_id: int, name: str, address: str):
        stmt = select(TheaterTable).where(TheaterTable.theater_id == theater_id)
        res = await db.execute(stmt)
        theater = res.scalars().first()
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        
        theater.name = name
        theater.address = address
        await db.commit()
        await db.refresh(theater)
        return theater

    @staticmethod
    async def delete_theater(db: AsyncSession, theater_id: int):
        stmt = select(TheaterTable).where(TheaterTable.theater_id == theater_id).options(selectinload(TheaterTable.rooms))
        res = await db.execute(stmt)
        theater = res.scalars().first()
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        
        if len(theater.rooms) > 0:
            raise HTTPException(status_code=400, detail="Cannot delete theater with existing rooms. Delete rooms first.")
            
        await db.delete(theater)
        await db.commit()
        return {"message": "Theater deleted successfully"}

    @staticmethod
    async def create_room(db: AsyncSession, theater_id: int, name: str, grid_rows: int, grid_cols: int, layout: dict):
        stmt = select(TheaterTable).where(TheaterTable.theater_id == theater_id)
        res = await db.execute(stmt)
        theater = res.scalars().first()
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")

        # Compute seat capacity from layout
        seat_capacity = sum(1 for type_ in layout.values() if type_ != 'empty')

        new_room = RoomTable(
            theater_id=theater_id, 
            name=name, 
            seat_capacity=seat_capacity,
            grid_rows=grid_rows,
            grid_cols=grid_cols
        )
        db.add(new_room)
        await db.flush() # get room_id

        # Create seats
        from src.models.theater import SeatTable
        seats_to_add = []
        for key, type_ in layout.items():
            if type_ != 'empty':
                row_char, col_str = key.split(':')
                seats_to_add.append(SeatTable(
                    room_id=new_room.room_id,
                    seat_row=row_char,
                    seat_num=int(col_str),
                    seat_type=type_
                ))
        
        for i in range(0, len(seats_to_add), 50):
            db.add_all(seats_to_add[i:i+50])
            await db.flush()
        
        await db.commit()
        await db.refresh(new_room)
        return new_room

    @staticmethod
    async def update_room_layout(db: AsyncSession, room_id: int, grid_rows: int, grid_cols: int, layout: dict):
        stmt = select(RoomTable).where(RoomTable.room_id == room_id)
        res = await db.execute(stmt)
        room = res.scalars().first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
            
        # Compute seat capacity from layout
        seat_capacity = sum(1 for type_ in layout.values() if type_ != 'empty')
        room.grid_rows = grid_rows
        room.grid_cols = grid_cols
        room.seat_capacity = seat_capacity

        from src.models.theater import SeatTable
        try:
            # Delete existing seats for this room
            await db.execute(delete(SeatTable).where(SeatTable.room_id == room_id))

            # Insert new seats
            seats_to_add = []
            for key, type_ in layout.items():
                if type_ != 'empty':
                    row_char, col_str = key.split(':')
                    seats_to_add.append(SeatTable(
                        room_id=room_id,
                        seat_row=row_char,
                        seat_num=int(col_str),
                        seat_type=type_
                    ))
            
            for i in range(0, len(seats_to_add), 50):
                db.add_all(seats_to_add[i:i+50])
                await db.flush()
                
            await db.commit()
            return {"message": "Room layout updated successfully"}
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Không thể thay đổi sơ đồ vì phòng này đã có lịch chiếu. Vui lòng xóa lịch chiếu trước.")

    @staticmethod
    async def delete_room(db: AsyncSession, room_id: int):
        stmt = select(RoomTable).where(RoomTable.room_id == room_id)
        res = await db.execute(stmt)
        room = res.scalars().first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
            
        from src.models.theater import SeatTable
        try:
            # Delete seats first to prevent basic FK constraint failure
            await db.execute(delete(SeatTable).where(SeatTable.room_id == room_id))
            # Delete the room
            await db.delete(room)
            await db.commit()
            return {"message": "Room deleted successfully"}
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Không thể xóa phòng chiếu này vì đã có lịch chiếu liên quan.")
