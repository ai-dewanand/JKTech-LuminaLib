import os
from fastapi import HTTPException, UploadFile
from typing import List
from sqlalchemy.orm import Session
from app.models.book import Book
from app.workers.tasks import generate_summary
from io import BytesIO
from PyPDF2 import PdfReader
import docx
from app.models.borrow import Borrow
from app.models.review import Review

# Directory for storing uploaded books
BOOKS_DIR = "data/books"
os.makedirs(BOOKS_DIR, exist_ok=True)

class BookService:
    def __init__(self):
        pass
    
    async def upload_book(self, title: str, author: str, description: str, file: UploadFile, db: Session):
        file_path = os.path.join(BOOKS_DIR, file.filename)
        file_bytes = await file.read()
        if file.filename.endswith(".pdf"):
            text = await self.extract_text_from_pdf(file_bytes)
        elif file.filename.endswith(".docx"):
            text = await self.extract_text_from_docx(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        # Save the file locally
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Create a new book record
        new_book = Book(title=title, author=author, description=description, file_path=file_path)
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        generate_summary.delay(new_book.id, text)

        return new_book
    
    async def extract_text_from_pdf(self, file_bytes):
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    async def extract_text_from_docx(self, file_bytes):
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    def list_books(self, db: Session) -> List[Book]:
        books = db.query(Book).all()
        return books

    def get_book(self, book_id: int, db: Session) -> Book:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    def update_book(
        self,
        book_id: int,
        db: Session,
        *,
        title: str | None = None,
        author: str | None = None,
        description: str | None = None,
    ) -> Book:
        book = self.get_book(book_id, db)

        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if description is not None:
            book.description = description

        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    def delete_book(self, book_id: int, db: Session) -> None:
        book = self.get_book(book_id, db)

        has_reviews = db.query(Review.id).filter(Review.book_id == book_id).first() is not None
        has_borrows = db.query(Borrow.id).filter(Borrow.book_id == book_id).first() is not None
        if has_reviews or has_borrows:
            raise HTTPException(
                status_code=409,
                detail="Book cannot be deleted because it has related borrows or reviews",
            )

        file_path = book.file_path
        db.delete(book)
        db.commit()

        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                # If file deletion fails, keep DB deletion as the source of truth.
                pass