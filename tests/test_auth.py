"""
Test cases for Authentication API endpoints.
"""
import pytest
from fastapi import status


class TestSignup:
    """Test cases for POST /auth/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
        assert "id" in data["user"]
        # Password should not be returned
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test signup with already registered email."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "Another User",
                "email": test_user.email,  # Already registered
                "password": "anotherpassword123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"
    
    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "Invalid User",
                "email": "invalid-email",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_signup_missing_name(self, client):
        """Test signup with missing name field."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "missing@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_signup_missing_password(self, client):
        """Test signup with missing password field."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "No Password User",
                "email": "nopassword@example.com"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_signup_empty_password(self, client):
        """Test signup with empty password."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "Empty Password User",
                "email": "emptypassword@example.com",
                "password": ""
            }
        )
        # Depending on validation, this might be 422 or could be allowed
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestLogin:
    """Test cases for POST /auth/login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Login successful"
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post(
            "/auth/login",
            json={
                "email": "invalid-email",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_email(self, client):
        """Test login with missing email field."""
        response = client.post(
            "/auth/login",
            json={
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login with missing password field."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_body(self, client):
        """Test login with empty request body."""
        response = client.post("/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenValidation:
    """Test cases for token authentication."""
    
    def test_valid_token_access(self, client, auth_headers, test_book):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/api/books", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_missing_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/books")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/books",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"
    
    def test_malformed_authorization_header(self, client):
        """Test accessing protected endpoint with malformed auth header."""
        response = client.get(
            "/api/books",
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_expired_token(self, client, test_user):
        """Test accessing protected endpoint with expired token."""
        from app.services.auth_service import create_access_token
        from datetime import timedelta
        
        # Create a token that's already expired
        expired_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=-1)  # Already expired
        )
        response = client.get(
            "/api/books",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Token has expired"
