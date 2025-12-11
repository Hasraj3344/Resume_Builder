"""Security utilities for password hashing and JWT tokens."""

import uuid
from datetime import datetime, timedelta
from typing import Tuple
from passlib.context import CryptContext
from jose import jwt, JWTError

from backend.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> Tuple[str, str, datetime]:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        tuple: (token, jti, expires_at)
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate unique token ID
    jti = str(uuid.uuid4())

    # Add claims
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "iat": datetime.utcnow()
    })

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt, jti, expire


def create_refresh_token(data: dict) -> Tuple[str, str, datetime]:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Payload data to encode in token

    Returns:
        tuple: (token, jti, expires_at)
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(data, expires_delta)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def validate_token(token: str) -> bool:
    """
    Validate a JWT token without raising exceptions.

    Args:
        token: JWT token string

    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        decode_token(token)
        return True
    except ValueError:
        return False
