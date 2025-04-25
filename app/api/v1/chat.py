from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import StartSessionRequest, StartSessionResponse, ChatRequest
from app.services.session import create_session, get_session, get_session_by_user
from app.core.ai.chat import process_chat_message
from app.services.database import get_db
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/start-session", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest, db: Session = Depends(get_db)):
    """Start a new session or recover an existing one"""
    try:
        # Always create a new session if is_new_chat is True
        if request.is_new_chat:
            session = create_session(request.user_id)
            return StartSessionResponse(
                session_id=session.session_id,
                message="Hi there! I'm Lila, your personal fragrance stylist. I'm here to help you discover your perfect scent that matches your personality and preferences. Would you mind sharing your name with me to get started?"
            )
        
        # For first-time users or when no existing session is found
        if request.user_id:
            existing_session = get_session_by_user(request.user_id)
            if existing_session:
                return StartSessionResponse(
                    session_id=existing_session.session_id,
                    message="Welcome back! Let's continue our journey to find your perfect fragrance. Is there anything specific you'd like to explore today?"
                )
        
        # Create new session for first-time users
        session = create_session(request.user_id)
        return StartSessionResponse(
            session_id=session.session_id,
            message="Hi there! I'm Lila, your personal fragrance stylist. I'm here to help you discover your perfect scent that matches your personality and preferences. Would you mind sharing your name with me to get started?"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Handle chat messages with streaming response"""
    try:
        # Verify session exists
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create async generator for streaming response
        async def generate():
            try:
                async for chunk in process_chat_message(request.session_id, request.message):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}")
                yield f"data: Error processing request. Please try again.\n\n"
            finally:
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 