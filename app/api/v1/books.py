from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from typing import List, Dict

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.services.book_service import BookService
from app.services.borrow_service import BorrowService
from app.services.review_service import ReviewService
from app.services.recommendation_service import RecommendationService
from app.schemas.book_schema import BookCreate, BookUpdate, BookResponse
from app.schemas.borrow_schema import BorrowUserRequest, BorrowResponse
from app.schemas.review_schema import ReviewUserCreate, ReviewResponse
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.core.logging import get_logger

# Router for book endpoints
books_router = APIRouter()

#Logging configuration
logger = get_logger(__name__)

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
async def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    book_service: BookService = Depends()
):
    """List books with pagination."""
    try:
        result = book_service.list_books(db, skip=skip, limit=limit)
        return JSONResponse(content={
            "books": [BookResponse.model_validate(book).model_dump() for book in result],
            "skip": skip,
            "limit": limit
        })
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


@books_router.post("/books/{book_id}/borrow", response_model=BorrowResponse)
async def borrow_book(
    book_id: int,
    request: BorrowUserRequest,
    db: Session = Depends(get_db),
    borrow_service: BorrowService = Depends(),
):
    """Borrow a book by ID."""
    try:
        borrow = borrow_service.borrow_book(request.user_id, book_id, db)
        payload = BorrowResponse.model_validate(borrow).model_dump(mode="json")
        logger.info(f"Book borrowed: User ID {request.user_id} borrowed Book ID {book_id}")
        return JSONResponse(content=jsonable_encoder({"borrowed": payload}))
    except HTTPException as e:
        logger.error(f"Error borrowing book: {e.detail}")
        raise e


@books_router.post("/books/{book_id}/return", response_model=BorrowResponse)
async def return_book(
    book_id: int,
    request: BorrowUserRequest,
    db: Session = Depends(get_db),
    borrow_service: BorrowService = Depends(),
):
    """Return a borrowed book by ID."""
    try:
        borrow = borrow_service.return_book(request.user_id, book_id, db)
        payload = BorrowResponse.model_validate(borrow).model_dump(mode="json")
        logger.info(f"Book returned: User ID {request.user_id} returned Book ID {book_id}")
        return JSONResponse(content=jsonable_encoder({"returned": payload}))
    except HTTPException as e:
        logger.error(f"Error returning book: {e.detail}")
        raise e


@books_router.post("/books/{book_id}/reviews", response_model=ReviewResponse)
async def submit_review(
    book_id: int,
    request: ReviewUserCreate,
    db: Session = Depends(get_db),
    review_service: ReviewService = Depends()
):
    """Submit a review for a book. User must have borrowed the book first."""
    try:
        review = review_service.submit_review(request.user_id, book_id, request.comment, request.rating, db)
        logger.info(f"Review submitted: User ID {request.user_id} reviewed Book ID {book_id}")
        return JSONResponse(content={"reviewed": ReviewResponse.model_validate(review).model_dump()})
    except HTTPException as e:
        logger.error(f"Error submitting review: {e.detail}")
        raise e


@books_router.get("/books/{book_id}/analysis", response_model=Dict)
async def get_book_analysis(
    book_id: int,
    db: Session = Depends(get_db)
):
    try:
        recommendation_service = RecommendationService(db)
        analysis = await recommendation_service.get_book_reviews_analysis(book_id)
        logger.info(f"Analysis retrieved for Book ID {book_id}")
        return analysis
    except HTTPException as e:
        logger.error(f"Error retrieving analysis for Book ID {book_id}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving analysis for Book ID {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")
