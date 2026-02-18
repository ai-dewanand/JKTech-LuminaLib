from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Borrow(Base):
    __tablename__ = 'borrows'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'))
    borrowed_at = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
    # Relationship
    book = relationship("Book", back_populates="borrows")