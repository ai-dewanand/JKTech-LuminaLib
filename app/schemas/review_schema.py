from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ReviewUserCreate(BaseModel):
    """Request body for review - only user_id needed, book_id comes from path."""
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(BaseModel):
    """Legacy request body with both user_id and book_id."""
    user_id: int
    book_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    comment: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)