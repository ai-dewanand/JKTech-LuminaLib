from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.services.borrow_service import BorrowService
from app.schemas.borrow_schema import BorrowRequest, BorrowResponse
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

borrow_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@borrow_router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(
    request: BorrowRequest,
    db: Session = Depends(get_db),
    borrow_service: BorrowService = Depends(),
):
    try:
        borrow = borrow_service.borrow_book(request.user_id, request.book_id, db)
        payload = BorrowResponse.model_validate(borrow).model_dump(mode="json")
        return JSONResponse(content=jsonable_encoder({"borrowed": payload}))
    except HTTPException as e:
        raise e

@borrow_router.post("/return", response_model=BorrowResponse)
async def return_book(
    request: BorrowRequest,
    db: Session = Depends(get_db),
    borrow_service: BorrowService = Depends(),
):
    try:
        borrow = borrow_service.return_book(request.user_id, request.book_id, db)
        payload = BorrowResponse.model_validate(borrow).model_dump(mode="json")
        return JSONResponse(content=jsonable_encoder({"returned": payload}))
    except HTTPException as e:
        raise e