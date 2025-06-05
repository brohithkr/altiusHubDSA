#!/usr/bin/env python3
"""
Comprehensive test script for the Books API with Authentication and Authorization
"""

import requests
import json
from datetime import date
from decimal import Decimal

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_api():
    print("🚀 Testing Books API with Authentication and Authorization")
    print("=" * 60)
    
    # Test data
    user1_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    user2_data = {
        "username": "jane_smith",
        "email": "jane@example.com",
        "password": "anothersecurepass456",
        "first_name": "Jane",
        "last_name": "Smith"
    }
    
    book_data = {
        "title": "The Art of Programming",
        "author": "John Doe",
        "isbn": "9781234567890",
        "publication_date": "2023-01-15",
        "pages": 350,
        "price": "29.99",
        "description": "A comprehensive guide to programming best practices"
    }
    
    book_data2 = {
        "title": "Advanced Algorithms",
        "author": "Jane Smith",
        "isbn": "9780987654321",
        "publication_date": "2023-06-01",
        "pages": 500,
        "price": "45.00",
        "description": "Deep dive into complex algorithms and data structures"
    }
    
    # Store tokens for authenticated requests
    user1_token = None
    user2_token = None
    
    print("\n1. 📝 Testing User Registration")
    print("-" * 30)
    
    # Register user 1
    response = requests.post(f"{BASE_URL}/auth/register", json=user1_data)
    if response.status_code == 200:
        result = response.json()
        user1_token = result["access_token"]
        print(f"✅ User 1 registered successfully: {result['user']['username']}")
        print(f"   Token: {user1_token[:50]}...")
    else:
        print(f"❌ User 1 registration failed: {response.text}")
    
    # Register user 2
    response = requests.post(f"{BASE_URL}/auth/register", json=user2_data)
    if response.status_code == 200:
        result = response.json()
        user2_token = result["access_token"]
        print(f"✅ User 2 registered successfully: {result['user']['username']}")
        print(f"   Token: {user2_token[:50]}...")
    else:
        print(f"❌ User 2 registration failed: {response.text}")
    
    print("\n2. 🔑 Testing User Login")
    print("-" * 30)
    
    # Test login with user 1
    login_data = {"username": user1_data["username"], "password": user1_data["password"]}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User 1 login successful")
        print(f"   User info: {result['user']['username']} ({result['user']['email']})")
    else:
        print(f"❌ User 1 login failed: {response.text}")
    
    print("\n3. 👤 Testing User Profile")
    print("-" * 30)
    
    # Get user profile
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Profile retrieved: {profile['username']}")
        print(f"   Email: {profile['email']}")
        print(f"   Staff: {profile['is_staff']}")
        print(f"   Admin: {profile['is_superuser']}")
    else:
        print(f"❌ Profile retrieval failed: {response.text}")
    
    print("\n4. 📚 Testing Book Creation (Authenticated)")
    print("-" * 30)
    
    book1_id = None
    book2_id = None
    
    # Create book with user 1
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers={"Authorization": f"Bearer {user1_token}"})
    if response.status_code == 200:
        result = response.json()
        book1_id = result["id"]
        print(f"✅ Book 1 created by user 1: ID {book1_id}")
    else:
        print(f"❌ Book 1 creation failed: {response.text}")
    
    # Create book with user 2
    response = requests.post(f"{BASE_URL}/books", json=book_data2, headers={"Authorization": f"Bearer {user2_token}"})
    if response.status_code == 200:
        result = response.json()
        book2_id = result["id"]
        print(f"✅ Book 2 created by user 2: ID {book2_id}")
    else:
        print(f"❌ Book 2 creation failed: {response.text}")
    
    # Try to create book without authentication
    response = requests.post(f"{BASE_URL}/books", json=book_data)
    if response.status_code == 401 or response.status_code == 422:
        print("✅ Book creation without auth properly rejected")
    else:
        print(f"❌ Book creation without auth should fail: {response.status_code}")
    
    print("\n5. 📖 Testing Book Retrieval (Public)")
    print("-" * 30)
    
    # Get all books (public)
    response = requests.get(f"{BASE_URL}/books")
    if response.status_code == 200:
        books = response.json()
        print(f"✅ Retrieved {len(books)} books publicly")
        for book in books:
            print(f"   - {book['title']} by {book['author']}")
    else:
        print(f"❌ Book retrieval failed: {response.text}")
    
    # Get specific book (public)
    if book1_id:
        response = requests.get(f"{BASE_URL}/books/{book1_id}")
        if response.status_code == 200:
            book = response.json()
            print(f"✅ Retrieved specific book: {book['title']}")
        else:
            print(f"❌ Specific book retrieval failed: {response.text}")
    
    print("\n6. ✏️  Testing Book Updates (Authorization)")
    print("-" * 30)
    
    # User 1 updates their own book
    update_data = {"title": "The Art of Advanced Programming", "price": "35.99"}
    if book1_id:
        response = requests.patch(f"{BASE_URL}/books/{book1_id}", json=update_data, headers={"Authorization": f"Bearer {user1_token}"})
        if response.status_code == 200:
            print("✅ User 1 successfully updated their own book")
        else:
            print(f"❌ User 1 book update failed: {response.text}")
    
    # User 2 tries to update User 1's book (should fail)
    if book1_id:
        response = requests.patch(f"{BASE_URL}/books/{book1_id}", json=update_data, headers={"Authorization": f"Bearer {user2_token}"})
        if response.status_code == 403:
            print("✅ User 2 correctly denied access to update User 1's book")
        else:
            print(f"❌ User 2 should not be able to update User 1's book: {response.status_code}")
    
    print("\n7. 🗑️  Testing Book Deletion (Authorization)")
    print("-" * 30)
    
    # User 2 tries to delete User 1's book (should fail)
    if book1_id:
        response = requests.delete(f"{BASE_URL}/books/{book1_id}", headers={"Authorization": f"Bearer {user2_token}"})
        if response.status_code == 403:
            print("✅ User 2 correctly denied access to delete User 1's book")
        else:
            print(f"❌ User 2 should not be able to delete User 1's book: {response.status_code}")
    
    # User 1 deletes their own book
    if book1_id:
        response = requests.delete(f"{BASE_URL}/books/{book1_id}", headers={"Authorization": f"Bearer {user1_token}"})
        if response.status_code == 200:
            print("✅ User 1 successfully deleted their own book")
        else:
            print(f"❌ User 1 book deletion failed: {response.text}")
    
    print("\n8. 👥 Testing User-Specific Endpoints")
    print("-" * 30)
    
    # Get current user's books
    response = requests.get(f"{BASE_URL}/my/books", headers={"Authorization": f"Bearer {user2_token}"})
    if response.status_code == 200:
        my_books = response.json()
        print(f"✅ User 2 has {len(my_books)} books")
    else:
        print(f"❌ My books retrieval failed: {response.text}")
    
    print("\n9. 🔍 Testing Search Features (Public)")
    print("-" * 30)
    
    # Search books
    response = requests.get(f"{BASE_URL}/books/search/algorithm")
    if response.status_code == 200:
        search_results = response.json()
        print(f"✅ Search found {len(search_results)} books with 'algorithm'")
    else:
        print(f"❌ Search failed: {response.text}")
    
    print("\n10. 🔄 Testing Token Refresh")
    print("-" * 30)
    
    # Test token refresh (assuming we have a refresh token)
    # Note: We'd need to modify the login response to include refresh token
    print("ℹ️  Token refresh test requires refresh token implementation")
    
    print("\n11. ⚠️  Testing Error Handling")
    print("-" * 30)
    
    # Test invalid token
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=invalid_headers)
    if response.status_code == 401 or response.status_code == 422:
        print("✅ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token should be rejected: {response.status_code}")
    
    # Test accessing non-existent book
    response = requests.get(f"{BASE_URL}/books/99999")
    if response.status_code == 404:
        print("✅ Non-existent book correctly returns 404")
    else:
        print(f"❌ Non-existent book should return 404: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
