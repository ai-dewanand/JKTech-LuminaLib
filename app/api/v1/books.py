from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List

from fastapi.responses import JSONResponse
from app.services.book_service import BookService
from app.schemas.book_schema import BookCreate, BookUpdate, BookResponse
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.core.logging import get_logger

# Router for book endpoints
books_router = APIRouter()

#Logging configuration
logger = get_logger(__name__)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@books_router.post("/books", response_model=BookResponse)
async def upload_book(
    book: BookCreate = Depends(),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    book_service: BookService = Depends(),
):
    try:
        new_book = await book_service.upload_book(book.title, book.author, book.description, file, db)
        logger.info(f"Book uploaded: {new_book.title} by {new_book.author}")
        return JSONResponse(content={"message": "Book uploaded successfully", 
                                     "book": BookResponse.model_validate(new_book).model_dump()})
    except HTTPException as e:
        logger.error(f"Error uploading book: {e.detail}")
        raise e


@books_router.get("/books", response_model=List[BookResponse])
async def list_books(db: Session = Depends(get_db), book_service: BookService = Depends()):
    try:
        result = book_service.list_books(db)
        return JSONResponse(content={"books": [BookResponse.model_validate(book).model_dump() for book in result]})
    except HTTPException as e:
        logger.error(f"Error listing books: {e.detail}")
        raise e
    
@books_router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    request: BookUpdate,
    db: Session = Depends(get_db),
    book_service: BookService = Depends(),
):
    try:
        updated = book_service.update_book(
            book_id,
            db,
            title=request.title,
            author=request.author,
            description=request.description,
        )
        logger.info(f"Book updated: {updated.title} by {updated.author}")
        return JSONResponse(
            content={
                "message": "Book updated successfully",
                "book": BookResponse.model_validate(updated).model_dump(),
            }
        )
    except HTTPException as e:
        logger.error(f"Error updating book: {e.detail}")
        raise e
    
@books_router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    book_service: BookService = Depends(),
):
    try:
        book_service.delete_book(book_id, db)
        logger.info(f"Book deleted: ID {book_id}")
        return JSONResponse(content={"message": "Book deleted successfully"})
    except HTTPException as e:
        logger.error(f"Error deleting book: {e.detail}")
        raise e
