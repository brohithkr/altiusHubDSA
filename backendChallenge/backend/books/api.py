from datetime import date, datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import jwt
from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.db.models import Q
from django.conf import settings
from .models import Book

# Initialize the API
api = NinjaAPI(title="Books API", description="RESTful CRUD API for managing books with authentication")

# Authentication utilities
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
            user_id = payload.get("user_id")
            if user_id:
                user = User.objects.get(id=user_id)
                return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None
        return None

def get_secret_key():
    return getattr(settings, 'SECRET_KEY', 'your-secret-key')

def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = timedelta(hours=24)
    else:
        expire = timedelta(hours=24)
    
    import datetime
    expire_time = datetime.datetime.utcnow() + expire
    
    to_encode = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "exp": expire_time
    }
    
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm="HS256")
    return encoded_jwt

def create_refresh_token(user: User) -> str:
    import datetime
    expire = datetime.datetime.utcnow() + timedelta(days=7)
    
    to_encode = {
        "user_id": user.id,
        "username": user.username,
        "type": "refresh",
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm="HS256")
    return encoded_jwt

def check_book_permissions(user: User, book) -> bool:
    return user == book.created_by or user.is_staff or user.is_superuser

auth = AuthBearer()

class BookIn(Schema):
    title: str
    author: str
    isbn: str
    publication_date: date
    pages: int
    price: Decimal
    description: Optional[str] = None

class BookOut(Schema):
    id: int
    title: str
    author: str
    isbn: str
    publication_date: date
    pages: int
    price: Decimal
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: int

class BookUpdate(Schema):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publication_date: Optional[date] = None
    pages: Optional[int] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None

class MessageResponse(Schema):
    message: str
    id: Optional[int] = None

class UserRegistration(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(Schema):
    username: str
    password: str

class TokenResponse(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class UserProfile(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_superuser: bool
    date_joined: datetime

@api.post("/auth/register", response=TokenResponse, tags=["Authentication"])
def register(request: HttpRequest, payload: UserRegistration):
    """Register a new user"""
    try:
        if User.objects.filter(username=payload.username).exists():
            return api.create_response(
                request,
                {"message": "Username already exists"},
                status=400,
            )
        
        if User.objects.filter(email=payload.email).exists():
            return api.create_response(
                request,
                {"message": "Email already exists"},
                status=400,
            )
        
        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name or "",
            last_name=payload.last_name or ""
        )
        
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser
            }
        }
    except Exception as e:
        return api.create_response(
            request,
            {"message": f"Registration failed: {str(e)}"},
            status=400,
        )

@api.post("/auth/login", response=TokenResponse, tags=["Authentication"])
def login(request: HttpRequest, payload: UserLogin):
    """Login user and return JWT tokens"""
    try:
        user = authenticate(username=payload.username, password=payload.password)
        
        if not user:
            return api.create_response(
                request,
                {"message": "Invalid credentials"},
                status=401,
            )
        
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser
            }
        }
    except Exception as e:
        return api.create_response(
            request,
            {"message": f"Login failed: {str(e)}"},
            status=400,
        )

@api.get("/auth/profile", response=UserProfile, auth=auth, tags=["Authentication"])
def get_profile(request: HttpRequest):
    """Get current user profile"""
    user = request.auth
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined
    }

@api.post("/books", response=MessageResponse, auth=auth, tags=["Books"])
def create_book(request: HttpRequest, payload: BookIn):
    """Create a new book (authenticated users only)"""
    try:
        user = request.auth
        book = Book.objects.create(**payload.dict(), created_by=user)
        return {"message": "Book created successfully", "id": book.id}
    except Exception as e:
        return {"message": f"Error creating book: {str(e)}"}

@api.get("/books/{book_id}", response=BookOut, tags=["Books"])
def get_book(request: HttpRequest, book_id: int):
    """Get a specific book by ID (public access)"""
    book = get_object_or_404(Book, id=book_id)
    return book

@api.get("/books", response=List[BookOut], tags=["Books"])
def list_books(request: HttpRequest, title: Optional[str] = None, author: Optional[str] = None):
    """List all books with optional filtering (public access)"""
    qs = Book.objects.all()
    
    if title:
        qs = qs.filter(title__icontains=title)
    if author:
        qs = qs.filter(author__icontains=author)
    
    return qs

@api.put("/books/{book_id}", response=MessageResponse, auth=auth, tags=["Books"])
def update_book(request: HttpRequest, book_id: int, payload: BookIn):
    """Update a book completely (owner or admin only)"""
    user = request.auth
    book = get_object_or_404(Book, id=book_id)
    
    if not check_book_permissions(user, book):
        return api.create_response(
            request,
            {"message": "You don't have permission to update this book"},
            status=403,
        )
    
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    
    book.save()
    return {"message": "Book updated successfully", "id": book.id}

@api.patch("/books/{book_id}", response=MessageResponse, auth=auth, tags=["Books"])
def partial_update_book(request: HttpRequest, book_id: int, payload: BookUpdate):
    """Partially update a book (owner or admin only)"""
    user = request.auth
    book = get_object_or_404(Book, id=book_id)
    
    if not check_book_permissions(user, book):
        return api.create_response(
            request,
            {"message": "You don't have permission to update this book"},
            status=403,
        )
    
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(book, attr, value)
    
    book.save()
    return {"message": "Book updated successfully", "id": book.id}

@api.delete("/books/{book_id}", response=MessageResponse, auth=auth, tags=["Books"])
def delete_book(request: HttpRequest, book_id: int):
    """Delete a book (owner or admin only)"""
    user = request.auth
    book = get_object_or_404(Book, id=book_id)
    
    if not check_book_permissions(user, book):
        return api.create_response(
            request,
            {"message": "You don't have permission to delete this book"},
            status=403,
        )
    
    book.delete()
    return {"message": "Book deleted successfully"}

# @api.get("/books/search/{query}", response=List[BookOut], tags=["Books"])
# def search_books(request: HttpRequest, query: str):
#     """Search books by title, author, or description (public access)"""
#     qs = Book.objects.filter(
#         Q(title__icontains=query) |
#         Q(author__icontains=query) |
#         Q(description__icontains=query)
#     )
#     return qs

# @api.get("/books/by-author/{author_name}", response=List[BookOut], tags=["Books"])
# def books_by_author(request: HttpRequest, author_name: str):
#     """Get all books by a specific author (public access)"""
#     qs = Book.objects.filter(author__icontains=author_name)
#     return qs

@api.get("/admin/books", response=List[BookOut], auth=auth, tags=["Admin"])
def admin_list_all_books(request: HttpRequest):
    """List all books (admin only)"""
    user = request.auth
    if not (user.is_staff or user.is_superuser):
        return api.create_response(
            request,
            {"message": "Admin access required"},
            status=403,
        )
    
    return Book.objects.all()

@api.get("/admin/users", response=List[UserProfile], auth=auth, tags=["Admin"])
def admin_list_users(request: HttpRequest):
    """List all users (admin only)"""
    user = request.auth
    if not user.is_superuser:
        return api.create_response(
            request,
            {"message": "Superuser access required"},
            status=403,
        )
    
    users = User.objects.all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "date_joined": u.date_joined
        }
        for u in users
    ]

@api.delete("/admin/books/{book_id}", response=MessageResponse, auth=auth, tags=["Admin"])
def admin_delete_book(request: HttpRequest, book_id: int):
    """Delete any book (admin only)"""
    user = request.auth
    if not (user.is_staff or user.is_superuser):
        return api.create_response(
            request,
            {"message": "Admin access required"},
            status=403,
        )
    
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return {"message": "Book deleted successfully by admin"}

# User's own books endpoints
@api.get("/my/books", response=List[BookOut], auth=auth, tags=["User Books"])
def my_books(request: HttpRequest):
    """Get current user's books"""
    user = request.auth
    return Book.objects.filter(created_by=user)

@api.get("/users/{user_id}/books", response=List[BookOut], tags=["User Books"])
def user_books(request: HttpRequest, user_id: int):
    """Get books by a specific user (public access)"""
    user = get_object_or_404(User, id=user_id)
    return Book.objects.filter(created_by=user)

# Error handlers
@api.exception_handler(Book.DoesNotExist)
def book_not_found(request, exc):
    return api.create_response(
        request,
        {"message": "Book not found"},
        status=404,
    )

@api.exception_handler(User.DoesNotExist)
def user_not_found(request, exc):
    return api.create_response(
        request,
        {"message": "User not found"},
        status=404,
    )

@api.exception_handler(ValueError)
def value_error(request, exc):
    return api.create_response(
        request,
        {"message": f"Invalid data: {str(exc)}"},
        status=400,
    )
