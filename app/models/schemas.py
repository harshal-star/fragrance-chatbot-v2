from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class StartSessionRequest(BaseModel):
    """Request model for starting a new session"""
    user_id: Optional[str] = None
    is_new_chat: bool = False

class StartSessionResponse(BaseModel):
    """Response model for session start"""
    session_id: str
    message: str

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    session_id: str
    message: str
    image_data: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    message: str = Field(..., description="The chat message")
    image_analysis: Optional[str] = Field(None, description="Image analysis results if an image was uploaded")
    session_id: str

class SessionContext(BaseModel):
    """Model for session context"""
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    last_interaction: Optional[str] = None
    conversation_stage: str = "initial"

class UserBase(BaseModel):
    """Base model for user"""
    name: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    """Model for creating a new user"""
    user_id: str

class User(UserBase):
    """Model for user response"""
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfileCreate(BaseModel):
    """Model for creating a user profile"""
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None

class UserProfileResponse(BaseModel):
    """Model for user profile response"""
    profile_id: int
    session_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScentPreferencesCreate(BaseModel):
    """Model for creating scent preferences"""
    favorite_fragrances: Optional[List[str]] = []
    preferred_notes: Optional[List[str]] = []
    disliked_notes: Optional[List[str]] = []
    preferred_seasons: Optional[List[str]] = []
    preferred_occasions: Optional[List[str]] = []

class ScentPreferencesResponse(BaseModel):
    """Model for scent preferences response"""
    preference_id: int
    session_id: str
    favorite_fragrances: Optional[List[str]] = []
    preferred_notes: Optional[List[str]] = []
    disliked_notes: Optional[List[str]] = []
    preferred_seasons: Optional[List[str]] = []
    preferred_occasions: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StylePreferencesCreate(BaseModel):
    """Model for creating style preferences"""
    fashion_style: Optional[str] = None
    preferred_colors: Optional[List[str]] = []
    preferred_materials: Optional[List[str]] = []
    preferred_brands: Optional[List[str]] = []

class StylePreferencesResponse(BaseModel):
    """Model for style preferences response"""
    style_id: int
    session_id: str
    fashion_style: Optional[str] = None
    preferred_colors: Optional[List[str]] = []
    preferred_materials: Optional[List[str]] = []
    preferred_brands: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PersonalityTraitsCreate(BaseModel):
    """Model for creating personality traits"""
    personality_type: Optional[str] = None
    interests: Optional[List[str]] = []
    lifestyle: Optional[str] = None
    values: Optional[List[str]] = []

class PersonalityTraitsResponse(BaseModel):
    """Model for personality traits response"""
    trait_id: int
    session_id: str
    personality_type: Optional[str] = None
    interests: Optional[List[str]] = []
    lifestyle: Optional[str] = None
    values: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ParseProfileRequest(BaseModel):
    """Request model for parsing user profile"""
    session_id: str
    conversation_history: List[Dict[str, str]]

class ParseProfileResponse(BaseModel):
    """Response model for parsed user profile"""
    user_id: str
    profile: UserProfileResponse
    scent_preferences: ScentPreferencesResponse
    style_preferences: StylePreferencesResponse
    personality_traits: PersonalityTraitsResponse

class SessionBase(BaseModel):
    """Base session model"""
    user_id: str
    conversation_history: Dict = Field(default_factory=lambda: {"messages": []})
    is_active: bool = True

class SessionCreate(SessionBase):
    """Session creation model"""
    pass

class SessionUpdate(BaseModel):
    """Session update model"""
    conversation_history: Optional[Dict] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = None

class SessionInDB(SessionBase):
    """Session database model"""
    session_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ImageUploadRequest(BaseModel):
    """Request model for image upload."""
    session_id: str = Field(..., description="The session ID")
    image_data: str = Field(..., description="Base64 encoded image data")
    message: Optional[str] = Field(None, description="Optional message with the image")

class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(..., description="The role of the message sender (user/assistant)")
    content: str = Field(..., description="The content of the message")
    timestamp: str = Field(..., description="ISO format timestamp of the message")
    image_analysis: Optional[Dict[str, Any]] = Field(None, description="Image analysis results if this is an image analysis message")

class ChatSession(BaseModel):
    """Model for chat sessions"""
    session_id: str = Field(..., description="Unique identifier for the session")
    user_id: str = Field(..., description="User ID associated with the session")
    conversation_history: Dict[str, List[ChatMessage]] = Field(
        default_factory=lambda: {"messages": []},
        description="The conversation history"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 