from pydantic import BaseModel
from typing import Optional, List, Dict
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

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    bot_message: str
    session_id: str

class SessionContext(BaseModel):
    """Model for session context"""
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    last_interaction: Optional[str] = None
    conversation_stage: str = "initial" 