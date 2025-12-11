"""Resume model for storing generated resumes."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base


class Resume(Base):
    """Resume model for storing user's generated resumes."""

    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    resume_data = Column(Text, nullable=False)  # JSON string of Resume model
    job_description_data = Column(Text, nullable=True)  # JSON string of JobDescription
    optimized_resume_data = Column(Text, nullable=True)  # JSON string of optimized Resume
    file_path = Column(String(500), nullable=True)  # Path to DOCX file
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.filename})>"
