from fastapi import APIRouter, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.recommendation_service import RecommendationService

# Router for recommendation endpoints
recommendation_router = APIRouter()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@recommendation_router.get("/recommendations", response_model=List[Dict])
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    recommendation_service = RecommendationService(db)
    return await recommendation_service.get_recommendations(user_id)