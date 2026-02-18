from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String)
    file_path = Column(String, nullable=False)
    summary = Column(String, nullable=True) 
    # Relationships
    reviews = relationship("Review", back_populates="book")
    borrows = relationship("Borrow", back_populates="book")

