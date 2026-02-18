"""
Test cases for root endpoint.
"""
import pytest
from fastapi import status


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Welcome to LuminaLib!"}
    
    def test_root_endpoint_method_not_allowed(self, client):
        """Test that POST to root is not allowed."""
        response = client.post("/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
