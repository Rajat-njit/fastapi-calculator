# app/models/user.py

"""
User SQLAlchemy model with:
- UUID primary key
- Unique username & email
- First/last name
- Password hashing helpers
- Authentication helper (authenticate)
- Timestamps & status flags
- Relationship to Calculation
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.models.calculation import GUID
from sqlalchemy import Column, String, Boolean, DateTime, or_
from sqlalchemy.orm import relationship, Session

from app.database import Base
from app.core.security import get_password_hash, verify_password, create_access_token


def utcnow() -> datetime:
    """Return current UTC time for DB timestamps."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    calculations = relationship("Calculation", back_populates="user", cascade="all, delete-orphan")


    # ---------------- Password helpers ----------------

    @property
    def hashed_password(self) -> str:
        return self.password

    def verify_password(self, plain_password: str) -> bool:
        """Check if a plain password matches the stored hash."""
        return verify_password(plain_password, self.password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using app's security settings."""
        return get_password_hash(password)

    # ---------------- Registration ----------------

    @classmethod
    def register(cls, db: Session, user_data: Dict[str, Any]) -> "User":
        """
        Register a new user.
        - Validates unique username/email.
        - Hashes the password.
        - Creates and returns the user (but does NOT commit).
        """
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")

        if not username or not email or not password:
            raise ValueError("Username, email, and password are required")

        # Check duplicates
        existing = (
            db.query(cls)
            .filter(or_(cls.username == username, cls.email == email))
            .first()
        )
        if existing:
            raise ValueError("Username or email already exists")

        user = cls(
            username=username,
            email=email,
            first_name=user_data.get("first_name", "").strip() or "First",
            last_name=user_data.get("last_name", "").strip() or "Last",
            password=cls.hash_password(password),
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        return user

    # ---------------- Authentication ----------------

    @classmethod
    def authenticate(
        cls,
        db: Session,
        username_or_email: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by username or email and password.
        Returns:
            {"user": user, "access_token": <jwt>} or None if invalid.
        """
        user = (
            db.query(cls)
            .filter(
                or_(
                    cls.username == username_or_email,
                    cls.email == username_or_email,
                )
            )
            .first()
        )

        if not user or not user.verify_password(password):
            return None

        # Update last_login
        user.last_login = utcnow()
        db.flush()

        access_token = create_access_token({"sub": str(user.id)})

        return {
            "user": user,
            "access_token": access_token,
        }
