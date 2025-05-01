from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Session(Base):
    """SQLAlchemy model for chat sessions."""
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)  # Make user_id nullable since we're using session-based auth
    conversation_history = Column(JSON, nullable=False, default=lambda: {"messages": []})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "conversation_history": self.conversation_history or {"messages": []},
            "created_at": self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else datetime.utcnow().isoformat()
        }

class User(Base):
    """SQLAlchemy model for users"""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    scent_preferences = relationship("ScentPreferences", back_populates="user", uselist=False)
    style_preferences = relationship("StylePreferences", back_populates="user", uselist=False)
    personality_traits = relationship("PersonalityTraits", back_populates="user", uselist=False)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class UserProfile(Base):
    """SQLAlchemy model for user profiles"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    age = Column(Integer)
    gender = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="profile")

    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "location": self.location,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class ScentPreferences(Base):
    """SQLAlchemy model for scent preferences"""
    __tablename__ = "scent_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    favorite_scents = Column(JSON, default=list)
    disliked_scents = Column(JSON, default=list)
    preferred_fragrance_families = Column(JSON, default=list)
    intensity_preference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="scent_preferences")

    def to_dict(self):
        """Convert scent preferences to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "favorite_scents": self.favorite_scents,
            "disliked_scents": self.disliked_scents,
            "preferred_fragrance_families": self.preferred_fragrance_families,
            "intensity_preference": self.intensity_preference,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class StylePreferences(Base):
    """SQLAlchemy model for style preferences"""
    __tablename__ = "style_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    style_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="style_preferences")

    def to_dict(self):
        """Convert style preferences to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "style_type": self.style_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class PersonalityTraits(Base):
    """SQLAlchemy model for personality traits"""
    __tablename__ = "personality_traits"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    traits = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="personality_traits")

    def to_dict(self):
        """Convert personality traits to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "traits": self.traits,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 