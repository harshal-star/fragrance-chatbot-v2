from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import UserProfile, ScentPreferences, StylePreferences, PersonalityTraits
from app.models.schemas import (
    UserProfileCreate,
    UserProfileResponse,
    ScentPreferencesCreate,
    ScentPreferencesResponse,
    StylePreferencesCreate,
    StylePreferencesResponse,
    PersonalityTraitsCreate,
    PersonalityTraitsResponse
)
from app.services.session import get_session

router = APIRouter(tags=["profile"])

@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile: UserProfileCreate,
    session_id: str,
    db: Session = Depends(get_db)
):
    session = get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db_profile = UserProfile(
        session_id=session_id,
        age=profile.age,
        gender=profile.gender,
        location=profile.location,
        occupation=profile.occupation
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.post("/scent-preferences", response_model=ScentPreferencesResponse)
async def create_scent_preferences(
    preferences: ScentPreferencesCreate,
    session_id: str,
    db: Session = Depends(get_db)
):
    session = get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db_preferences = ScentPreferences(
        session_id=session_id,
        favorite_fragrances=preferences.favorite_fragrances,
        preferred_notes=preferences.preferred_notes,
        disliked_notes=preferences.disliked_notes,
        preferred_seasons=preferences.preferred_seasons,
        preferred_occasions=preferences.preferred_occasions
    )
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

@router.post("/style-preferences", response_model=StylePreferencesResponse)
async def create_style_preferences(
    preferences: StylePreferencesCreate,
    session_id: str,
    db: Session = Depends(get_db)
):
    session = get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db_preferences = StylePreferences(
        session_id=session_id,
        fashion_style=preferences.fashion_style,
        preferred_colors=preferences.preferred_colors,
        preferred_materials=preferences.preferred_materials,
        preferred_brands=preferences.preferred_brands
    )
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

@router.post("/personality-traits", response_model=PersonalityTraitsResponse)
async def create_personality_traits(
    traits: PersonalityTraitsCreate,
    session_id: str,
    db: Session = Depends(get_db)
):
    session = get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db_traits = PersonalityTraits(
        session_id=session_id,
        personality_type=traits.personality_type,
        interests=traits.interests,
        lifestyle=traits.lifestyle,
        values=traits.values
    )
    db.add(db_traits)
    db.commit()
    db.refresh(db_traits)
    return db_traits 