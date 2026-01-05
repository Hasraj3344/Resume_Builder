"""Authentication service for user registration and login."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.models.subscription import Subscription
from backend.models.session import Session as SessionModel
from backend.utils.security import hash_password, verify_password, create_access_token
from backend.config import settings


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        full_name: str = None,
        phone: str = None,
        address: str = None,
        profile_pic_path: str = None,
        resume_file_path: str = None,
        resume_text: str = None,
        resume_parsed_data: dict = None
    ) -> User:
        """
        Register a new user with optional profile and resume data.

        Args:
            db: Database session
            email: User email
            password: Plain text password
            full_name: Optional full name
            phone: Optional phone number
            address: Optional address
            profile_pic_path: Optional profile picture file path
            resume_file_path: Optional resume file path
            resume_text: Optional resume text content
            resume_parsed_data: Optional parsed resume data as dict

        Returns:
            User: Created user

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hash_password(password)

        # Create user with all data
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            address=address,
            profile_pic_path=profile_pic_path,
            resume_file_path=resume_file_path,
            resume_text=resume_text,
            resume_parsed_data=resume_parsed_data,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create free subscription for new user
        subscription = Subscription(
            user_id=user.id,
            plan_type="free",
            status="active"
        )

        db.add(subscription)
        db.commit()

        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User: Authenticated user

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    @staticmethod
    def create_user_session(db: Session, user: User):
        """
        Create a new session with access token for user.

        Args:
            db: Database session
            user: User to create session for

        Returns:
            tuple: (access_token, jti, expires_at)
        """
        # Create access token
        token_data = {
            "sub": user.id,
            "email": user.email
        }

        access_token, jti, expires_at = create_access_token(token_data)

        # Store session in database
        session = SessionModel(
            user_id=user.id,
            token_jti=jti,
            expires_at=expires_at,
            revoked=False
        )

        db.add(session)
        db.commit()

        return access_token, jti, expires_at

    @staticmethod
    def revoke_session(db: Session, token_jti: str):
        """
        Revoke a user session.

        Args:
            db: Database session
            token_jti: Token JTI to revoke
        """
        session = db.query(SessionModel).filter(
            SessionModel.token_jti == token_jti
        ).first()

        if session:
            session.revoked = True
            db.commit()

    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: str):
        """
        Revoke all sessions for a user.

        Args:
            db: Database session
            user_id: User ID
        """
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked == False
        ).all()

        for session in sessions:
            session.revoked = True

        db.commit()

    @staticmethod
    def cleanup_expired_sessions(db: Session):
        """
        Clean up expired sessions from database.

        Args:
            db: Database session
        """
        expired_sessions = db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow()
        ).all()

        for session in expired_sessions:
            db.delete(session)

        db.commit()

        return len(expired_sessions)
