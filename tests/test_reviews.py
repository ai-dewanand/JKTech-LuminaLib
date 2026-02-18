"""
Test cases for Reviews API endpoints.
"""
import pytest
from fastapi import status


class TestSubmitReview:
    """Test cases for POST /reviews/reviews endpoint."""
    
    def test_submit_review_success(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test successful review submission (requires prior borrow)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 5,
                "comment": "Excellent book!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reviewed" in data
        assert data["reviewed"]["user_id"] == test_user.id
        assert data["reviewed"]["book_id"] == test_book.id
        assert data["reviewed"]["rating"] == 5
        assert data["reviewed"]["comment"] == "Excellent book!"
    
    def test_submit_review_without_comment(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review submission without comment (comment is optional)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 4
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reviewed"]["rating"] == 4
        assert data["reviewed"]["comment"] is None
    
    def test_submit_review_minimum_rating(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review with minimum rating (1)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 1,
                "comment": "Not recommended"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["reviewed"]["rating"] == 1
    
    def test_submit_review_maximum_rating(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review with maximum rating (5)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 5,
                "comment": "Highly recommended!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["reviewed"]["rating"] == 5
    
    def test_submit_review_rating_below_minimum(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review with rating below minimum (0)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 0,
                "comment": "Invalid rating"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_rating_above_maximum(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review with rating above maximum (6)."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 6,
                "comment": "Invalid rating"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_negative_rating(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review with negative rating."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": -1,
                "comment": "Negative rating"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_nonexistent_user(self, client, auth_headers, test_book):
        """Test review submission with non-existent user."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": 99999,
                "book_id": test_book.id,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
    
    def test_submit_review_nonexistent_book(self, client, auth_headers, test_user):
        """Test review submission for non-existent book."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": 99999,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
    
    def test_submit_review_without_auth(self, client, test_user, test_book):
        """Test review submission without authentication."""
        response = client.post(
            "/reviews/reviews",
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_submit_review_missing_user_id(self, client, auth_headers, test_book):
        """Test review submission with missing user_id."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "book_id": test_book.id,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_missing_book_id(self, client, auth_headers, test_user):
        """Test review submission with missing book_id."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_missing_rating(self, client, auth_headers, test_user, test_book):
        """Test review submission with missing rating."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_invalid_user_id(self, client, auth_headers, test_book):
        """Test review submission with invalid user_id format."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": "invalid",
                "book_id": test_book.id,
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_invalid_book_id(self, client, auth_headers, test_user):
        """Test review submission with invalid book_id format."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": "invalid",
                "rating": 4,
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_invalid_rating_type(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review submission with invalid rating type."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": "excellent",
                "comment": "Test comment"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_review_float_rating(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review submission with float rating."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 4.5,
                "comment": "Test comment"
            }
        )
        # FastAPI might truncate to int or return validation error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_submit_review_empty_comment(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review submission with empty comment."""
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 4,
                "comment": ""
            }
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_submit_review_long_comment(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test review submission with a long comment."""
        long_comment = "A" * 10000  # 10000 character comment
        response = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 4,
                "comment": long_comment
            }
        )
        # Should succeed unless there's a length limit
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestMultipleReviews:
    """Test cases for multiple review scenarios."""
    
    def test_multiple_reviews_same_book_different_users(self, client, auth_headers, test_user, test_user2, test_book, test_borrow, db_session):
        """Test multiple users reviewing the same book (requires borrow first)."""
        from app.models.borrow import Borrow
        from datetime import datetime
        
        # Create borrow for test_user2
        borrow2 = Borrow(user_id=test_user2.id, book_id=test_book.id, borrowed_at=datetime.utcnow())
        db_session.add(borrow2)
        db_session.commit()
        
        # First user review
        response1 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 5,
                "comment": "Great book!"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second user review
        response2 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user2.id,
                "book_id": test_book.id,
                "rating": 3,
                "comment": "It was okay"
            }
        )
        assert response2.status_code == status.HTTP_200_OK
    
    def test_same_user_review_multiple_books(self, client, auth_headers, test_user, test_book, test_book2, test_borrow, db_session):
        """Test same user reviewing multiple books (requires borrow first)."""
        from app.models.borrow import Borrow
        from datetime import datetime
        
        # Create borrow for test_book2
        borrow2 = Borrow(user_id=test_user.id, book_id=test_book2.id, borrowed_at=datetime.utcnow())
        db_session.add(borrow2)
        db_session.commit()
        
        # Review first book
        response1 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 5,
                "comment": "Loved the first book!"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Review second book
        response2 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book2.id,
                "rating": 4,
                "comment": "Second book was good too"
            }
        )
        assert response2.status_code == status.HTTP_200_OK
    
    def test_duplicate_review_same_user_same_book(self, client, auth_headers, test_user, test_book, test_borrow):
        """Test if same user can submit multiple reviews for the same book."""
        # First review
        response1 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 5,
                "comment": "First review"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second review for same book by same user
        response2 = client.post(
            "/reviews/reviews",
            headers=auth_headers,
            json={
                "user_id": test_user.id,
                "book_id": test_book.id,
                "rating": 3,
                "comment": "Changed my mind"
            }
        )
        # Business logic may allow or prevent duplicate reviews
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]
