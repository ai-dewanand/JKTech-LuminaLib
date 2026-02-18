from celery import Celery
import asyncio
# Import all models to ensure SQLAlchemy can resolve relationships
from app.models import Book, Review, Borrow, User
from app.services.ai_service import AIService
from app.core.database import SessionLocal

# Initialize Celery app
celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def generate_summary(book_id: int, content: str):
    try:
        db = SessionLocal()
        # AIService.summarize is async, so we need to run it with asyncio
        summary = asyncio.run(AIService().summarize(content))
        if summary:
            print(f"Generated summary for book {book_id}: {summary}")
            book = db.query(Book).filter(Book.id == book_id).first()
            if book:
                book.summary = summary
                db.commit()
        else:
            print(f"Failed to generate summary for book {book_id}")
    except Exception as e:
        print(f"Error generating summary for book {book_id}: {e}")
    finally:
        db.close()