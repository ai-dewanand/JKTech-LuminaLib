from pydantic import BaseModel, ConfigDict

class BookCreate(BaseModel):
    title: str
    author: str
    description: str

class BookUpdate(BaseModel):
  title: str | None = None
  author: str | None = None
  description: str | None = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str
    summary: str | None = None 

    model_config = ConfigDict(from_attributes=True)