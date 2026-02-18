# Import all models here so SQLAlchemy can resolve relationships
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.models.borrow import Borrow
from app.models.user_preference import UserPreference

__all__ = ["User", "Book", "Review", "Borrow", "UserPreference"]
