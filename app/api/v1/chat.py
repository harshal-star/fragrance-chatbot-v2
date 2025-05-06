from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse, ImageUploadRequest
from app.services.chat import ChatService
from app.database import get_db
from fastapi.responses import StreamingResponse, JSONResponse
import logging
from typing import List, Dict, Optional
from app.core.config import settings
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)

class StartSessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    message_id: Optional[str] = None
    image_data: Optional[str] = None  # base64 or URL, depending on frontend

router = APIRouter(tags=["chat"])

@router.post("/start-session", response_model=Dict)
async def start_session(request: StartSessionRequest, db: Session = Depends(get_db)):
    """Start a new chat session."""
    try:
        chat_service = ChatService(db, settings)
        return await chat_service.start_chat(request.user_id)
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Process a chat message and stream the response, or return JSON for image uploads."""
    print(30 * "------------")
    print("WE ARE IN CHAT ENDPOINT!!")
    print(30 * "------------")
    try:
        chat_service = ChatService(db, settings)
        # If image_data is present, use non-streaming
        if request.image_data:
            result = await chat_service.process_message(request.session_id, request.message, request.image_data, request.message_id)
            print("Returning image analysis result:", result)
            return JSONResponse(content=result)
        # Otherwise, stream as usual
        return StreamingResponse(
            chat_service.process_message_stream(
                request.session_id, request.message, background_tasks, request.image_data, request.message_id
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/history/{session_id}")
async def get_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session."""
    try:
        chat_service = ChatService(db, settings)
        history = await chat_service.get_chat_history(session_id)
        return {"messages": history}
    except ValueError as e:
        logger.error(f"Session not found: {str(e)}")
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

@router.get("/sessions/{user_id}")
async def list_sessions(user_id: str, db: Session = Depends(get_db)):
    """List all chat sessions for a user."""
    from app.services.session import get_session_by_user
    from app.models.models import Session as SessionModel
    # Print the absolute path of the database file (for SQLite)
    try:
        db_url = db.bind.url.database if hasattr(db.bind.url, 'database') else str(db.bind.url)
        print('DEBUG: Database file in use:', os.path.abspath(db_url))
    except Exception as e:
        print('DEBUG: Could not determine database file path:', e)
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).order_by(SessionModel.updated_at.desc()).all()
    print('DEBUG: Session IDs for', user_id, ':', [s.session_id for s in sessions])
    session_list = []
    for s in sessions:
        messages = s.conversation_history.get("messages", [])
        preview = messages[-1]["content"] if messages else ""
        session_list.append({
            "session_id": s.session_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "preview": preview
        })
    return session_list 