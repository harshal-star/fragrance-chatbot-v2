import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
import asyncio
from app.models.schemas import SessionContext
from app.services.database import get_db, save_session, get_session_by_id, get_session_by_user_id, DBSession, delete_session
from app.core.utils import logger

# Session configuration
SESSION_TIMEOUT = timedelta(hours=24)  # Sessions expire after 24 hours
CLEANUP_INTERVAL = timedelta(hours=1)  # Run cleanup every hour

# In-memory session storage (replace with database in production)
sessions: Dict[str, SessionContext] = {}

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def create_session(user_id: Optional[str] = None) -> SessionContext:
    """Create a new session"""
    session_id = generate_session_id()
    session = SessionContext(
        session_id=session_id,
        user_id=user_id,
        conversation_history=[],
        last_interaction=datetime.now().isoformat(),
        conversation_stage="initial"
    )
    
    # Save to database
    db = next(get_db())
    save_session(db, session)
    
    logger.info(f"Created new session: {session_id} for user: {user_id}")
    return session

def get_session(session_id: str) -> Optional[SessionContext]:
    """Get an existing session"""
    db = next(get_db())
    db_session = get_session_by_id(db, session_id)
    
    if db_session:
        # Check if session has expired
        last_interaction = db_session.last_interaction
        if datetime.now() - last_interaction > SESSION_TIMEOUT:
            logger.info(f"Session {session_id} has expired")
            delete_session(db, session_id)
            return None
            
        return SessionContext(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            conversation_history=db_session.conversation_history,
            last_interaction=db_session.last_interaction.isoformat(),
            conversation_stage=db_session.conversation_stage
        )
    return None

def get_session_by_user(user_id: str) -> Optional[SessionContext]:
    """Get a session by user ID"""
    db = next(get_db())
    db_session = get_session_by_user_id(db, user_id)
    
    if db_session:
        # Check if session has expired
        last_interaction = db_session.last_interaction
        if datetime.now() - last_interaction > SESSION_TIMEOUT:
            logger.info(f"Session {db_session.session_id} for user {user_id} has expired")
            delete_session(db, db_session.session_id)
            return None
            
        return SessionContext(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            conversation_history=db_session.conversation_history,
            last_interaction=db_session.last_interaction.isoformat(),
            conversation_stage=db_session.conversation_stage
        )
    return None

def update_session(session: SessionContext) -> None:
    """Update an existing session"""
    db = next(get_db())
    save_session(db, session)
    logger.debug(f"Updated session: {session.session_id}")

def delete_session(session_id: str) -> None:
    """Delete a session"""
    db = next(get_db())
    if delete_session(db, session_id):
        logger.info(f"Deleted session: {session_id}")
    else:
        logger.warning(f"Attempted to delete non-existent session: {session_id}")

async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    while True:
        try:
            db = next(get_db())
            expired_sessions = db.query(DBSession).filter(
                DBSession.last_interaction < datetime.now() - SESSION_TIMEOUT
            ).all()
            
            for session in expired_sessions:
                delete_session(db, session.session_id)
                logger.info(f"Cleaned up expired session: {session.session_id}")
                
            logger.info(f"Session cleanup completed. Removed {len(expired_sessions)} expired sessions")
        except Exception as e:
            logger.error(f"Error during session cleanup: {str(e)}", exc_info=True)
        
        await asyncio.sleep(CLEANUP_INTERVAL.total_seconds()) 