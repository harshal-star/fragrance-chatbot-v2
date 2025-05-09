from datetime import datetime, timedelta
import uuid
import asyncio
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.models import Session, User
from app.core.utils import logger
from sqlalchemy import text, inspect

# Session configuration
SESSION_TIMEOUT = timedelta(hours=24)  # Sessions expire after 24 hours
CLEANUP_INTERVAL = timedelta(hours=1)  # Run cleanup every hour

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def create_session(user_id: Optional[str] = None, db: Session = None) -> Dict:
    """Create a new chat session for a user, and ensure the user exists."""
    try:
        # Ensure user exists
        if user_id:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                user = User(user_id=user_id)
                db.add(user)
                db.commit()
        session_id = generate_session_id(); now = datetime.utcnow()
        session = Session(
            session_id=session_id,
            user_id=user_id,
            conversation_history={"messages": []},
            created_at=now,
            updated_at=now
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session.to_dict()
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise

def get_session(session_id: str, db: Session) -> Optional[Dict]:
    """Get a session by ID."""
    try:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        if not session:
            return None
        return session.to_dict()
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise

def get_session_by_user(user_id: str, db: Session) -> Optional[Dict]:
    """Get a session by user ID."""
    try:
        session = db.query(Session).filter(Session.user_id == user_id).first()
        if not session:
            return None
        return session.to_dict()
    except Exception as e:
        logger.error(f"Error getting session by user: {str(e)}")
        raise

def save_session(session_id: str, user_id: Optional[str], session_data: Dict, db: Session) -> None:
    """Save session data."""
    try:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        now = datetime.utcnow()
        
        if not session:
            session = Session(
                session_id=session_id,
                user_id=user_id,
                conversation_history=session_data.get("conversation_history", {"messages": []}),
                created_at=now,
                updated_at=now
            )
            db.add(session)
        else:
            session.conversation_history = session_data.get("conversation_history", {"messages": []})
            session.updated_at = now
            
        db.commit()
    except Exception as e:
        logger.error(f"Error saving session: {str(e)}")
        raise

def table_exists(db: Session, table_name: str) -> bool:
    inspector = inspect(db.bind)
    return table_name in inspector.get_table_names()

def cleanup_expired_sessions(db: Session) -> None:
    """Clean up expired sessions."""
    try:
        if table_exists(db, "sessions"):
            expired_time = datetime.utcnow() - timedelta(hours=24)
            db.query(Session).filter(Session.updated_at < expired_time).delete()
            db.commit()
        else:
            logger.warning("sessions table does not exist yet, skipping cleanup.")
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}")
        raise

async def run_cleanup_task(db: Session) -> None:
    """Run the cleanup task periodically."""
    try:
        while True:
            try:
                cleanup_expired_sessions(db)
                logger.info("Successfully cleaned up expired sessions")
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
            
            # Sleep for the cleanup interval
            await asyncio.sleep(CLEANUP_INTERVAL.total_seconds())
    except asyncio.CancelledError:
        logger.info("Cleanup task cancelled")
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise 