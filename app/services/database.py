from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import SessionLocal, DBSession

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_session(db: Session, session_data):
    """Save or update a session in the database"""
    db_session = db.query(DBSession).filter(DBSession.session_id == session_data.session_id).first()
    
    if db_session:
        # Update existing session
        db_session.conversation_history = session_data.conversation_history
        db_session.last_interaction = datetime.fromisoformat(session_data.last_interaction)
        db_session.conversation_stage = session_data.conversation_stage
    else:
        # Create new session
        db_session = DBSession(
            session_id=session_data.session_id,
            user_id=session_data.user_id,
            conversation_history=session_data.conversation_history,
            last_interaction=datetime.fromisoformat(session_data.last_interaction),
            conversation_stage=session_data.conversation_stage
        )
        db.add(db_session)
    
    db.commit()
    return db_session

def get_session_by_id(db: Session, session_id: str):
    """Retrieve a session by its ID"""
    return db.query(DBSession).filter(DBSession.session_id == session_id).first()

def get_session_by_user_id(db: Session, user_id: str):
    """Retrieve a session by user ID"""
    return db.query(DBSession).filter(DBSession.user_id == user_id).first()

def delete_session(db: Session, session_id: str):
    """Delete a session"""
    db_session = db.query(DBSession).filter(DBSession.session_id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False 