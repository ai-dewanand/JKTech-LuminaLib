from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int

class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
