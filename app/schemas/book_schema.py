from pydantic import BaseModel, ConfigDict

class BookCreate(BaseModel):
    title: str
    author: str
    description: str
      # Added description field to match the upload_book endpoint


class BookUpdate(BaseModel):
  title: str | None = None
  author: str | None = None
  description: str | None = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str
    summary: str | None = None  # Include summary in the response

    model_config = ConfigDict(from_attributes=True)