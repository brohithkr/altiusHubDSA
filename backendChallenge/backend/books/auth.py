import jwt
from datetime import datetime, timedelta
from typing import Optional, Any
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ninja.security import HttpBearer
from ninja import Schema


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
    """Get JWT secret key from Django settings"""
    return getattr(settings, 'SECRET_KEY', 'your-secret-key')


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token for user"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm="HS256")
    return encoded_jwt


def create_refresh_token(user: User) -> str:
    """Create JWT refresh token for user"""
    expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {
        "user_id": user.id,
        "username": user.username,
        "type": "refresh",
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm="HS256")
    return encoded_jwt


def verify_password(user: User, password: str) -> bool:
    """Verify user password"""
    return user.check_password(password)


def get_user_from_token(token: str) -> Optional[User]:
    """Extract user from JWT token"""
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id:
            return User.objects.get(id=user_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None
    return None


# Schemas for authentication
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
    date_joined: str


class RefreshTokenRequest(Schema):
    refresh_token: str


# Role checking utilities
def is_admin_or_staff(user: User) -> bool:
    """Check if user is admin or staff"""
    return user.is_superuser or user.is_staff


def is_owner_or_admin(user: User, resource_owner: User) -> bool:
    """Check if user is owner of resource or admin"""
    return user == resource_owner or is_admin_or_staff(user)


def check_book_permissions(user: User, book) -> bool:
    """Check if user has permissions to modify a book"""
    return is_owner_or_admin(user, book.created_by)
