from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Explicit preferences (user-defined)
    favorite_genres = Column(String, nullable=True)  # Comma-separated genres
    favorite_authors = Column(String, nullable=True)  # Comma-separated authors
    
    # Implicit preferences (system-derived from behavior)
    preferred_reading_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    avg_rating_given = Column(Float, nullable=True)  # Average rating user gives
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
