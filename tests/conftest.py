"""
Pytest configuration and fixtures for LuminaLib API tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import io
from PyPDF2 import PdfWriter
from app.main import app
from app.core.database import Base, SessionLocal
from app.models.user import User
from app.models.book import Book
from app.models.borrow import Borrow
from app.models.review import Review
from app.services.auth_service import get_password_hash, create_access_token
from datetime import timedelta

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    from app.api.v1.auth import get_db as auth_get_db
    from app.api.v1.books import get_db as books_get_db
    from app.api.v1.borrow import get_db as borrow_get_db
    from app.api.v1.reviews import get_db as reviews_get_db
    from app.api.v1.recommendations import get_db as recommendations_get_db
    
    def override_get_db_for_test():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[auth_get_db] = override_get_db_for_test
    app.dependency_overrides[books_get_db] = override_get_db_for_test
    app.dependency_overrides[borrow_get_db] = override_get_db_for_test
    app.dependency_overrides[reviews_get_db] = override_get_db_for_test
    app.dependency_overrides[recommendations_get_db] = override_get_db_for_test
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    hashed_password = get_password_hash("testpassword123")
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hashed_password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Create a second test user in the database."""
    hashed_password = get_password_hash("testpassword456")
    user = User(
        name="Test User 2",
        email="test2@example.com",
        hashed_password=hashed_password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Generate a valid authentication token for test user."""
    access_token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return access_token


@pytest.fixture
def auth_headers(auth_token):
    """Return authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_book(db_session):
    """Create a test book in the database."""
    book = Book(
        title="Test Book",
        author="Test Author",
        description="A test book description",
        file_path="/tmp/test_book.pdf",
        summary="Test summary"
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book


@pytest.fixture
def test_book2(db_session):
    """Create a second test book in the database."""
    book = Book(
        title="Another Test Book",
        author="Another Author",
        description="Another test book description",
        file_path="/tmp/another_test_book.pdf",
        summary="Another test summary"
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book


@pytest.fixture
def test_borrow(db_session, test_user, test_book):
    """Create a test borrow record."""
    from datetime import datetime
    borrow = Borrow(
        user_id=test_user.id,
        book_id=test_book.id,
        borrowed_at=datetime.utcnow()
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(borrow)
    return borrow


@pytest.fixture
def test_review(db_session, test_user, test_book):
    """Create a test review."""
    review = Review(
        user_id=test_user.id,
        book_id=test_book.id,
        rating=5,
        comment="Great book!"
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    return review


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing book uploads."""
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=612, height=792)
    
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    
    return ("test_book.pdf", pdf_bytes, "application/pdf")
