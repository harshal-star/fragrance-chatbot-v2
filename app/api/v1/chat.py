from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse, ImageUploadRequest
from app.services.chat import ChatService
from app.database import get_db
from fastapi.responses import StreamingResponse
import logging
from typing import List, Dict
from app.core.config import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class StartSessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

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
    """Process a chat message and stream the response."""
    try:
        chat_service = ChatService(db, settings)
        return StreamingResponse(
            chat_service.process_message_stream(
                request.session_id, request.message, background_tasks
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
        chat_service = ChatService(db)
        history = await chat_service.get_chat_history(session_id)
        return {"messages": history}
    except ValueError as e:
        logger.error(f"Session not found: {str(e)}")
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat history") 