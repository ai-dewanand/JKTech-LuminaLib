from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.models.review import Review
from app.services.review_service import ReviewService
from app.schemas.review_schema import ReviewCreate, ReviewResponse
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

# Router for review endpoints
review_router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@review_router.post("/reviews", response_model=ReviewResponse)
async def submit_review(request: ReviewCreate,
                         db: Session = Depends(get_db),
                           review_service: ReviewService = Depends()):
    try:
        review = review_service.submit_review(request.user_id, request.book_id, request.comment, request.rating, db)
        return JSONResponse(content={"reviewed": ReviewResponse.model_validate(review).model_dump()})
    except HTTPException as e:
        raise e