from sqlalchemy.orm import Session
from app.models.review import Review as ReviewModel
from app.models.borrow import Borrow as BorrowModel
from app.services.borrow_service import BorrowService
from app.core.database import SessionLocal
from datetime import datetime
from fastapi import HTTPException

class ReviewService:
    def __init__(self):
        pass

    def submit_review(self, user_id: int, book_id: int, review_text: str, rating: int, db: Session):
        # Check if the user has borrowed the book
        borrow = BorrowService.can_review(self, user_id, book_id, db=db)
        if not borrow:
            raise HTTPException(status_code=400, detail="User has not borrowed this book")
        # Create a new review record
        new_review = ReviewModel(
            user_id=user_id,
            book_id=book_id,
            comment=review_text,
            rating=rating,
        )
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review