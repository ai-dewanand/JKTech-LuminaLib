from sqlalchemy.orm import Session
from app.models.borrow import Borrow  # SQLAlchemy model
from datetime import datetime
from fastapi import HTTPException

class BorrowService:
    def __init__(self):
        pass

    def borrow_book(self, user_id: int, book_id: int, db: Session):
        try:
            # Check if the book is already borrowed and not returned
            existing_borrow = (
                db.query(Borrow)
                .filter(Borrow.book_id == book_id, Borrow.returned_at == None)
                .first()
            )
            if existing_borrow:
                raise HTTPException(status_code=400, detail="Book is already borrowed")

            # Create a new borrow record
            new_borrow = Borrow(
                user_id=user_id,
                book_id=book_id,
                borrowed_at=datetime.now(),
                returned_at=None,
            )
            db.add(new_borrow)
            db.commit()
            db.refresh(new_borrow)
            return new_borrow
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def return_book(self, user_id: int, book_id: int, db: Session):
        try:
            # Find the borrow record
            borrow = (
                db.query(Borrow)
                .filter(
                    Borrow.user_id == user_id,
                    Borrow.book_id == book_id,
                    Borrow.returned_at == None,
                )
                .first()
            )
            if not borrow:
                raise HTTPException(status_code=400, detail="No active borrow record found")
            borrow.returned_at = datetime.now()
            db.commit()
            db.refresh(borrow)
            return borrow
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def can_review(self, user_id: int, book_id: int, db: Session):
        try:
            # Check if the user has borrowed the book
            borrow = (
                db.query(Borrow)
                .filter(Borrow.user_id == user_id, Borrow.book_id == book_id)
                .first()
            )
            return borrow is not None
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))