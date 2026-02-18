from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi import security
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer
from app.core.config import settings
from app.models.user import User 
from sqlalchemy.orm import Session
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.core.logging import get_logger
from app.core.database import get_db


# Router for authentication endpoints
auth_router = APIRouter()
app_security = HTTPBearer()

#logging configuration
logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT (use environment variables in production)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_token(credentials: HTTPAuthorizationCredentials = Security(app_security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload  # Return the decoded token payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# Endpoints
@auth_router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Attempt to register with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(user.password)
        new_user = User(hashed_password=hashed_password, email=user.email, name=user.name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        response = JSONResponse(content={"message": "User created successfully", "user": UserResponse.model_validate(new_user).model_dump()})
        return response
    except HTTPException as e:
        logger.error(f"Signup error: {e.detail}")
        raise e


@auth_router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        response = JSONResponse(content={"message": "Login successful","user": UserResponse.model_validate(db_user).model_dump(), "access_token": access_token})
        return response
    except HTTPException as e:
        logger.error(f"Login error: {e.detail}")
        raise e