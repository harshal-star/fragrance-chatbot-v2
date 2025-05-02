from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.models import User as UserModel
from app.core.utils import logger
from datetime import datetime
from app.models.schemas import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user: UserCreate) -> dict:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.query(UserModel).filter(
                UserModel.user_id == user.user_id
            ).first()

            if existing_user:
                return existing_user.to_dict()

            # Create new user
            new_user = UserModel(
                user_id=user.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            return new_user.to_dict()
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self.db.rollback()
            raise

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get a user by ID"""
        try:
            user = self.db.query(UserModel).filter(
                UserModel.user_id == user_id
            ).first()
            
            if not user:
                return None
                
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise

    async def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict]:
        """
        Update a user's information
        """
        try:
            user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return None

            if name is not None:
                user.name = name
            if email is not None:
                user.email = email

            self.db.commit()
            self.db.refresh(user)

            return {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise 