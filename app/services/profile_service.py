from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime
from app.models.models import (
    User as UserModel,
    UserProfile as UserProfileModel,
    ScentPreferences as ScentPreferencesModel,
    StylePreferences as StylePreferencesModel,
    PersonalityTraits as PersonalityTraitsModel
)
from app.models.schemas import (
    UserCreate, UserProfileCreate, ScentPreferencesCreate,
    StylePreferencesCreate, PersonalityTraitsCreate
)
from app.core.utils import logger

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user: UserCreate) -> Dict:
        """Create a new user"""
        try:
            # Check if user exists
            existing_user = self.db.query(UserModel).filter(
                UserModel.user_id == user.user_id
            ).first()
            
            if existing_user:
                return existing_user.to_dict()

            # Create new user
            db_user = UserModel(
                user_id=user.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user.to_dict()
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self.db.rollback()
            raise

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return None
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise

    async def create_user_profile(self, user_id: str, profile_data: UserProfileCreate) -> Dict:
        """Create a new user profile"""
        try:
            # Check if user exists
            user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # Create profile
            profile = UserProfileModel(
                user_id=user_id,
                age=profile_data.age,
                gender=profile_data.gender,
                location=profile_data.location
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            return profile.to_dict()
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            self.db.rollback()
            raise

    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get a user's complete profile"""
        try:
            # Get user
            user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return None

            # Get profile data
            profile = self.db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
            scent_prefs = self.db.query(ScentPreferencesModel).filter(ScentPreferencesModel.user_id == user_id).first()
            style_prefs = self.db.query(StylePreferencesModel).filter(StylePreferencesModel.user_id == user_id).first()
            personality = self.db.query(PersonalityTraitsModel).filter(PersonalityTraitsModel.user_id == user_id).first()

            return {
                "user": user.to_dict(),
                "profile": profile.to_dict() if profile else None,
                "scent_preferences": scent_prefs.to_dict() if scent_prefs else None,
                "style_preferences": style_prefs.to_dict() if style_prefs else None,
                "personality_traits": personality.to_dict() if personality else None
            }
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    async def create_scent_preferences(self, preferences: ScentPreferencesCreate) -> Dict:
        """Create scent preferences for a user"""
        try:
            # Check if user exists
            user = self.db.query(UserModel).filter(UserModel.user_id == preferences.user_id).first()
            if not user:
                raise ValueError("User not found")

            # Check if preferences already exist
            existing_prefs = self.db.query(ScentPreferencesModel).filter(
                ScentPreferencesModel.user_id == preferences.user_id
            ).first()

            if existing_prefs:
                # Update existing preferences
                existing_prefs.favorite_scents = list(set(existing_prefs.favorite_scents + preferences.favorite_scents))
                existing_prefs.disliked_scents = list(set(existing_prefs.disliked_scents + preferences.disliked_scents))
                existing_prefs.preferred_fragrance_families = list(set(existing_prefs.preferred_fragrance_families + preferences.preferred_fragrance_families))
                existing_prefs.intensity_preference = preferences.intensity_preference
                existing_prefs.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_prefs)
                return existing_prefs.to_dict()

            # Create new preferences
            scent_prefs = ScentPreferencesModel(
                user_id=preferences.user_id,
                favorite_scents=preferences.favorite_scents,
                disliked_scents=preferences.disliked_scents,
                preferred_fragrance_families=preferences.preferred_fragrance_families,
                intensity_preference=preferences.intensity_preference,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(scent_prefs)
            self.db.commit()
            self.db.refresh(scent_prefs)
            
            return scent_prefs.to_dict()
        except Exception as e:
            logger.error(f"Error creating scent preferences: {str(e)}")
            self.db.rollback()
            raise

    async def get_scent_preferences(self, user_id: str) -> Optional[Dict]:
        """Get scent preferences by user ID"""
        try:
            prefs = self.db.query(ScentPreferencesModel).filter(
                ScentPreferencesModel.user_id == user_id
            ).first()
            if not prefs:
                return None
            return prefs.to_dict()
        except Exception as e:
            logger.error(f"Error getting scent preferences: {str(e)}")
            raise

    async def create_style_preferences(self, preferences: StylePreferencesCreate) -> Dict:
        """Create style preferences for a user"""
        try:
            # Check if user exists
            user = self.db.query(UserModel).filter(UserModel.user_id == preferences.user_id).first()
            if not user:
                raise ValueError("User not found")

            # Check if preferences already exist
            existing_prefs = self.db.query(StylePreferencesModel).filter(
                StylePreferencesModel.user_id == preferences.user_id
            ).first()

            if existing_prefs:
                # Update existing preferences
                existing_prefs.clothing_style = preferences.clothing_style
                existing_prefs.all_styles = list(set(existing_prefs.all_styles + preferences.all_styles))
                existing_prefs.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_prefs)
                return existing_prefs.to_dict()

            # Create new preferences
            style_prefs = StylePreferencesModel(
                user_id=preferences.user_id,
                clothing_style=preferences.clothing_style,
                all_styles=preferences.all_styles,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(style_prefs)
            self.db.commit()
            self.db.refresh(style_prefs)
            
            return style_prefs.to_dict()
        except Exception as e:
            logger.error(f"Error creating style preferences: {str(e)}")
            self.db.rollback()
            raise

    async def get_style_preferences(self, user_id: str) -> Optional[Dict]:
        """Get style preferences by user ID"""
        try:
            prefs = self.db.query(StylePreferencesModel).filter(
                StylePreferencesModel.user_id == user_id
            ).first()
            if not prefs:
                return None
            return prefs.to_dict()
        except Exception as e:
            logger.error(f"Error getting style preferences: {str(e)}")
            raise

    async def create_personality_traits(self, user_id: str, traits: PersonalityTraitsCreate) -> Dict:
        """Create personality traits for a user"""
        try:
            # Check if user exists
            user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # Create traits
            personality = PersonalityTraitsModel(
                user_id=user_id,
                traits=traits.traits
            )
            
            self.db.add(personality)
            self.db.commit()
            self.db.refresh(personality)
            
            return personality.to_dict()
        except Exception as e:
            logger.error(f"Error creating personality traits: {str(e)}")
            self.db.rollback()
            raise

    def get_personality_traits(self, user_id: str) -> Optional[Dict]:
        """Get personality traits by user ID"""
        try:
            traits = self.db.query(PersonalityTraitsModel).filter(PersonalityTraitsModel.user_id == user_id).first()
            if not traits:
                return None
            return traits.to_dict()
        except Exception as e:
            logger.error(f"Error getting personality traits: {str(e)}")
            raise

    def update_user_profile(self, user_id: str, profile_data: dict) -> Optional[Dict]:
        """Update user profile"""
        try:
            profile = self.db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
            if not profile:
                return None

            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            profile.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(profile)
            return profile.to_dict()
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            self.db.rollback()
            raise

    async def update_scent_preferences(self, user_id: str, preferences_data: dict) -> Optional[Dict]:
        """Update scent preferences"""
        try:
            prefs = self.db.query(ScentPreferencesModel).filter(
                ScentPreferencesModel.user_id == user_id
            ).first()
            if not prefs:
                return None

            # Merge preferences
            if 'favorite_scents' in preferences_data:
                existing = set(prefs.favorite_scents or [])
                new = set(preferences_data['favorite_scents'] or [])
                prefs.favorite_scents = list(existing.union(new))

            if 'disliked_scents' in preferences_data:
                existing = set(prefs.disliked_scents or [])
                new = set(preferences_data['disliked_scents'] or [])
                prefs.disliked_scents = list(existing.union(new))

            if 'preferred_fragrance_families' in preferences_data:
                existing = set(prefs.preferred_fragrance_families or [])
                new = set(preferences_data['preferred_fragrance_families'] or [])
                prefs.preferred_fragrance_families = list(existing.union(new))

            if 'intensity_preference' in preferences_data:
                prefs.intensity_preference = preferences_data['intensity_preference']

            prefs.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(prefs)
            return prefs.to_dict()
        except Exception as e:
            logger.error(f"Error updating scent preferences: {str(e)}")
            self.db.rollback()
            raise

    async def update_style_preferences(self, user_id: str, preferences_data: dict) -> Optional[Dict]:
        """Update style preferences"""
        try:
            prefs = self.db.query(StylePreferencesModel).filter(
                StylePreferencesModel.user_id == user_id
            ).first()
            if not prefs:
                return None

            # Update preferences
            if 'clothing_style' in preferences_data:
                prefs.clothing_style = preferences_data['clothing_style']

            if 'all_styles' in preferences_data:
                existing = set(prefs.all_styles or [])
                new = set(preferences_data['all_styles'] or [])
                prefs.all_styles = list(existing.union(new))

            prefs.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(prefs)
            return prefs.to_dict()
        except Exception as e:
            logger.error(f"Error updating style preferences: {str(e)}")
            self.db.rollback()
            raise

    def update_personality_traits(self, user_id: str, traits_data: dict) -> Optional[Dict]:
        """Update personality traits"""
        try:
            traits = self.db.query(PersonalityTraitsModel).filter(PersonalityTraitsModel.user_id == user_id).first()
            if not traits:
                return None

            for key, value in traits_data.items():
                if hasattr(traits, key):
                    setattr(traits, key, value)

            traits.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(traits)
            return traits.to_dict()
        except Exception as e:
            logger.error(f"Error updating personality traits: {str(e)}")
            self.db.rollback()
            raise 