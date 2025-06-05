#!/usr/bin/env python3
"""
Test script for the Books CRUD API using Django Ninja
"""

import requests
import json
from datetime import date

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_create_book():
    """Test creating a new book"""
    print("1. Testing CREATE book...")
    
    book_data = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "publication_date": "1925-04-10",
        "pages": 180,
        "price": "12.99",
        "description": "A classic American novel set in the Jazz Age"
    }
    
    response = requests.post(f"{BASE_URL}/books", json=book_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get("id")

def test_get_book(book_id):
    """Test getting a specific book"""
    print(f"\n2. Testing GET book with ID {book_id}...")
    
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_books():
    """Test listing all books"""
    print("\n3. Testing LIST all books...")
    
    response = requests.get(f"{BASE_URL}/books")
    print(f"Status: {response.status_code}")
    books = response.json()
    print(f"Found {len(books)} books:")
    for book in books:
        print(f"  - {book['title']} by {book['author']}")

def test_update_book(book_id):
    """Test updating a book"""
    print(f"\n4. Testing UPDATE book with ID {book_id}...")
    
    update_data = {
        "title": "The Great Gatsby (Updated)",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "publication_date": "1925-04-10",
        "pages": 180,
        "price": "15.99",
        "description": "A classic American novel set in the Jazz Age - Updated edition"
    }
    
    response = requests.put(f"{BASE_URL}/books/{book_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_partial_update_book(book_id):
    """Test partially updating a book"""
    print(f"\n5. Testing PARTIAL UPDATE book with ID {book_id}...")
    
    update_data = {
        "price": "18.99"
    }
    
    response = requests.patch(f"{BASE_URL}/books/{book_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_search_books():
    """Test searching books"""
    print("\n6. Testing SEARCH books...")
    
    response = requests.get(f"{BASE_URL}/books/search/Gatsby")
    print(f"Status: {response.status_code}")
    books = response.json()
    print(f"Found {len(books)} books matching 'Gatsby':")
    for book in books:
        print(f"  - {book['title']} by {book['author']}")

def test_delete_book(book_id):
    """Test deleting a book"""
    print(f"\n7. Testing DELETE book with ID {book_id}...")
    
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def create_sample_books():
    """Create some sample books for testing"""
    print("Creating sample books...")
    
    sample_books = [
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "isbn": "9780446310789",
            "publication_date": "1960-07-11",
            "pages": 281,
            "price": "14.99",
            "description": "A story of racial injustice and childhood innocence"
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "9780451524935",
            "publication_date": "1949-06-08",
            "pages": 328,
            "price": "13.99",
            "description": "A dystopian social science fiction novel"
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "isbn": "9780141439518",
            "publication_date": "1813-01-28",
            "pages": 432,
            "price": "11.99",
            "description": "A romantic novel of manners"
        }
    ]
    
    for book in sample_books:
        response = requests.post(f"{BASE_URL}/books", json=book)
        if response.status_code == 200:
            print(f"Created: {book['title']}")
        else:
            print(f"Failed to create: {book['title']}")

if __name__ == "__main__":
    print("Testing Books CRUD API")
    print("=" * 50)
    
    try:
        # Create sample books first
        create_sample_books()
        
        # Test CRUD operations
        book_id = test_create_book()
        
        if book_id:
            test_get_book(book_id)
            test_list_books()
            test_update_book(book_id)
            test_partial_update_book(book_id)
            test_search_books()
            
            # Verify the book was updated
            test_get_book(book_id)
            
            # Finally delete the book
            test_delete_book(book_id)
            
            # Verify it was deleted
            print(f"\n8. Verifying book {book_id} was deleted...")
            response = requests.get(f"{BASE_URL}/books/{book_id}")
            print(f"Status: {response.status_code} (should be 404)")
        
        print("\n" + "=" * 50)
        print("API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the Django server is running at http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error: {e}")
