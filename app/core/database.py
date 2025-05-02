from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db(db: Session) -> None:
    """Initialize database tables"""
    try:
        # Check if personality_traits table exists
        table_exists = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='personality_traits'
        """)).fetchone()

        if not table_exists:
            # Create table with all columns
            db.execute(text("""
                CREATE TABLE personality_traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    traits JSON,
                    primary_trait TEXT,
                    confidence_score JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """))
            logger.info("Created personality_traits table")
        else:
            # Check for missing columns
            columns = db.execute(text("""
                PRAGMA table_info(personality_traits)
            """)).fetchall()
            column_names = [col[1] for col in columns]

            if 'primary_trait' not in column_names:
                db.execute(text("""
                    ALTER TABLE personality_traits 
                    ADD COLUMN primary_trait TEXT
                """))
                logger.info("Added primary_trait column to personality_traits table")

            if 'confidence_score' not in column_names:
                db.execute(text("""
                    ALTER TABLE personality_traits 
                    ADD COLUMN confidence_score JSON
                """))
                logger.info("Added confidence_score column to personality_traits table")

        db.commit()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        db.rollback()
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 