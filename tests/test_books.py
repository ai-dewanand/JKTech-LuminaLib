"""
Test cases for Books API endpoints.
"""
import pytest
from fastapi import status
import io


class TestListBooks:
    """Test cases for GET /api/books endpoint."""
    
    def test_list_books_empty(self, client, auth_headers):
        """Test listing books when no books exist."""
        response = client.get("/api/books", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "books" in data
        assert data["books"] == []
    
    def test_list_books_with_data(self, client, auth_headers, test_book, test_book2):
        """Test listing books when books exist."""
        response = client.get("/api/books", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "books" in data
        assert len(data["books"]) == 2
        
        # Verify book structure
        book = data["books"][0]
        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "description" in book
    
    def test_list_books_without_auth(self, client):
        """Test listing books without authentication."""
        response = client.get("/api/books")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

from unittest.mock import patch


class TestUploadBook:
    """Test cases for POST /api/books endpoint."""
    
    @patch('app.services.book_service.generate_summary')
    def test_upload_book_success(self, mock_generate_summary, client, auth_headers, sample_pdf_file):
        """Test successful book upload with PDF file."""
        filename, file_content, content_type = sample_pdf_file
        
        response = client.post(
            "/api/books",
            headers=auth_headers,
            params={
                "title": "New Book",
                "author": "New Author",
                "description": "A new book description"
            },
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Book uploaded successfully"
        assert data["book"]["title"] == "New Book"
        assert data["book"]["author"] == "New Author"
        assert data["book"]["description"] == "A new book description"
        # Verify that the celery task was called
        mock_generate_summary.delay.assert_called_once()
    
    def test_upload_book_without_file(self, client, auth_headers):
        """Test book upload without file."""
        response = client.post(
            "/api/books",
            headers=auth_headers,
            params={
                "title": "Book Without File",
                "author": "Author",
                "description": "Description"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_book_missing_title(self, client, auth_headers, sample_pdf_file):
        """Test book upload with missing title."""
        filename, file_content, content_type = sample_pdf_file
        
        response = client.post(
            "/api/books",
            headers=auth_headers,
            params={
                "author": "Author",
                "description": "Description"
            },
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_book_missing_author(self, client, auth_headers, sample_pdf_file):
        """Test book upload with missing author."""
        filename, file_content, content_type = sample_pdf_file
        
        response = client.post(
            "/api/books",
            headers=auth_headers,
            params={
                "title": "Title",
                "description": "Description"
            },
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_book_missing_description(self, client, auth_headers, sample_pdf_file):
        """Test book upload with missing description."""
        filename, file_content, content_type = sample_pdf_file
        
        response = client.post(
            "/api/books",
            headers=auth_headers,
            params={
                "title": "Title",
                "author": "Author"
            },
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_book_without_auth(self, client, sample_pdf_file):
        """Test book upload without authentication."""
        filename, file_content, content_type = sample_pdf_file
        
        response = client.post(
            "/api/books",
            params={
                "title": "Book",
                "author": "Author",
                "description": "Description"
            },
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestUpdateBook:
    """Test cases for PUT /api/books/{book_id} endpoint."""
    
    def test_update_book_success(self, client, auth_headers, test_book):
        """Test successful book update."""
        response = client.put(
            f"/api/books/{test_book.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "author": "Updated Author",
                "description": "Updated Description"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Book updated successfully"
        assert data["book"]["title"] == "Updated Title"
        assert data["book"]["author"] == "Updated Author"
        assert data["book"]["description"] == "Updated Description"
    
    def test_update_book_partial(self, client, auth_headers, test_book):
        """Test partial book update (only title)."""
        original_author = test_book.author
        original_description = test_book.description
        
        response = client.put(
            f"/api/books/{test_book.id}",
            headers=auth_headers,
            json={
                "title": "Only Title Updated"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["book"]["title"] == "Only Title Updated"
    
    def test_update_book_not_found(self, client, auth_headers):
        """Test updating non-existent book."""
        response = client.put(
            "/api/books/99999",
            headers=auth_headers,
            json={
                "title": "Updated Title"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_book_without_auth(self, client, test_book):
        """Test book update without authentication."""
        response = client.put(
            f"/api/books/{test_book.id}",
            json={
                "title": "Updated Title"
            }
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_update_book_invalid_id(self, client, auth_headers):
        """Test updating book with invalid ID format."""
        response = client.put(
            "/api/books/invalid",
            headers=auth_headers,
            json={
                "title": "Updated Title"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteBook:
    """Test cases for DELETE /api/books/{book_id} endpoint."""
    
    def test_delete_book_success(self, client, auth_headers, test_book, db_session):
        """Test successful book deletion."""
        book_id = test_book.id
        
        response = client.delete(
            f"/api/books/{book_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Book deleted successfully"
        
        # Verify book is actually deleted
        list_response = client.get("/api/books", headers=auth_headers)
        books = list_response.json()["books"]
        assert not any(book["id"] == book_id for book in books)
    
    def test_delete_book_not_found(self, client, auth_headers):
        """Test deleting non-existent book."""
        response = client.delete(
            "/api/books/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_book_without_auth(self, client, test_book):
        """Test book deletion without authentication."""
        response = client.delete(f"/api/books/{test_book.id}")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_delete_book_invalid_id(self, client, auth_headers):
        """Test deleting book with invalid ID format."""
        response = client.delete(
            "/api/books/invalid",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_already_deleted_book(self, client, auth_headers, test_book):
        """Test deleting a book that was already deleted."""
        book_id = test_book.id
        
        # First deletion should succeed
        response1 = client.delete(f"/api/books/{book_id}", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second deletion should fail
        response2 = client.delete(f"/api/books/{book_id}", headers=auth_headers)
        assert response2.status_code == status.HTTP_404_NOT_FOUND
