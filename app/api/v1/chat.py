from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse, ImageUploadRequest
from app.services.chat import ChatService
from app.database import get_db
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

@router.post("/start-session", response_model=ChatResponse)
async def start_session(request: dict = None, db: Session = Depends(get_db)):
    """Start a new chat session."""
    try:
        chat_service = ChatService(db)
        # Use provided user_id or generate a new one
        user_id = request.get("user_id") if request else None
        result = await chat_service.start_chat(user_id)
        return ChatResponse(
            message=result["message"],
            session_id=result["session_id"]
        )
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start chat session")

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat message."""
    try:
        chat_service = ChatService(db)
        session = chat_service.get_session(request.session_id, db)
        if not session:
            raise ValueError("Session not found")

        # Process message with image data if provided
        if hasattr(request, 'image_data') and request.image_data:
            result = await chat_service.process_message(
                request.session_id,
                request.message,
                request.image_data
            )
            return ChatResponse(
                message=result["message"],
                image_analysis=result.get("analysis", ""),
                session_id=request.session_id
            )

        # For regular messages, stream the response
        async def generate():
            try:
                async for chunk in chat_service.generate_response(session, request.message, db):
                    if chunk:
                        yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}")
                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except ValueError as e:
        logger.error(f"Session not found: {str(e)}")
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

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