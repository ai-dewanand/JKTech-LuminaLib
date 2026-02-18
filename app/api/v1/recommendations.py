from http.client import HTTPException
from fastapi import APIRouter, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.recommendation_service import RecommendationService
from app.core.logging import get_logger

# Router for recommendation endpoints
recommendation_router = APIRouter()

#logging configuration
logger = get_logger(__name__) 

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
    try:
            recommendation_service = RecommendationService(db)
            recommendations = await recommendation_service.get_recommendations(user_id)
            logger.info(f"Recommendations retrieved for User ID {user_id}")
            return recommendations
    except Exception as e:
        logger.error(f"Error retrieving recommendations for User ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving recommendations for User ID {user_id}, {e}")