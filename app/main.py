from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from app.api.v1.auth import auth_router
from app.api.v1.books import books_router
from app.api.v1.recommendations import recommendation_router
from app.api.v1.auth import verify_token


app = FastAPI(
    title="LuminaLib",
    description="An intelligent library system",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints for user authentication",
        },
        {
            "name": "Books",
            "description": "Endpoints for managing books",
        },
    ],
)


app.include_router(auth_router, prefix="/auth")
# Protect all non-auth routes with verify_token dependency
app.include_router(books_router, prefix="/api", dependencies=[Depends(verify_token)])
app.include_router(recommendation_router, prefix="/recommendations", dependencies=[Depends(verify_token)])

@app.get("/")
def read_root():
    return {"message": "Welcome to LuminaLib!"}