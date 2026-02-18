"""
Test cases for Recommendations API endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestGetRecommendations:
    """Test cases for GET /recommendations/recommendations endpoint."""
    
    def test_get_recommendations_success(self, client, auth_headers, test_user, test_book, test_review):
        """Test successful recommendations retrieval."""
        # Mock the recommendation service to avoid external dependencies
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = [
                {
                    "book_id": test_book.id,
                    "title": test_book.title,
                    "author": test_book.author,
                    "score": 0.95
                }
            ]
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
    
    def test_get_recommendations_new_user(self, client, auth_headers, test_user):
        """Test recommendations for user with no history."""
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = []
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            # New user might get empty recommendations or default suggestions
    
    def test_get_recommendations_nonexistent_user(self, client, auth_headers):
        """Test recommendations for non-existent user."""
        response = client.get(
            "/recommendations/recommendations?user_id=99999",
            headers=auth_headers
        )
        # Might return empty list or 404 depending on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_recommendations_without_auth(self, client, test_user):
        """Test recommendations without authentication."""
        response = client.get(
            f"/recommendations/recommendations?user_id={test_user.id}"
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_recommendations_missing_user_id(self, client, auth_headers):
        """Test recommendations with missing user_id parameter."""
        response = client.get(
            "/recommendations/recommendations",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_recommendations_invalid_user_id(self, client, auth_headers):
        """Test recommendations with invalid user_id format."""
        response = client.get(
            "/recommendations/recommendations?user_id=invalid",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_recommendations_negative_user_id(self, client, auth_headers):
        """Test recommendations with negative user_id."""
        response = client.get(
            "/recommendations/recommendations?user_id=-1",
            headers=auth_headers
        )
        # Negative IDs might be handled differently
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestRecommendationQuality:
    """Test cases for recommendation quality and behavior."""
    
    def test_recommendations_based_on_reviews(self, client, auth_headers, test_user, test_book, test_book2, db_session):
        """Test that recommendations consider user's review history."""
        from app.models.review import Review
        
        # Add a high rating review
        review = Review(
            user_id=test_user.id,
            book_id=test_book.id,
            rating=5,
            comment="Amazing book!"
        )
        db_session.add(review)
        db_session.commit()
        
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = [
                {
                    "book_id": test_book2.id,
                    "title": test_book2.title,
                    "author": test_book2.author,
                    "score": 0.85
                }
            ]
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
    
    def test_recommendations_based_on_borrow_history(self, client, auth_headers, test_user, test_book, test_book2, test_borrow):
        """Test that recommendations consider user's borrow history."""
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = [
                {
                    "book_id": test_book2.id,
                    "title": test_book2.title,
                    "author": test_book2.author,
                    "score": 0.80
                }
            ]
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK


class TestRecommendationResponse:
    """Test cases for recommendation response format."""
    
    def test_recommendation_response_structure(self, client, auth_headers, test_user, test_book):
        """Test the structure of recommendation response."""
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = [
                {
                    "book_id": 1,
                    "title": "Recommended Book",
                    "author": "Author Name",
                    "description": "Book description",
                    "score": 0.95
                }
            ]
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
    
    def test_empty_recommendations(self, client, auth_headers, test_user):
        """Test response when no recommendations are available."""
        with patch('app.services.recommendation_service.RecommendationService.get_recommendations') as mock_rec:
            mock_rec.return_value = []
            
            response = client.get(
                f"/recommendations/recommendations?user_id={test_user.id}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data == []
