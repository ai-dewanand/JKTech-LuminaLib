from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'))
    rating = Column(Integer, nullable=False)  # Removed minimum and maximum, use Pydantic for validation
    comment = Column(String, nullable=True)

    # Relationship
    book = relationship("Book", back_populates="reviews")