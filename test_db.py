import sqlite3
import os
import asyncio
from datetime import datetime
from app.database import SessionLocal, init_db
from app.services.user import UserService
from app.services.chat import ChatService
from app.core.utils import logger

async def test_database():
    """Test database operations"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized")

        # Create a database session
        db = SessionLocal()
        try:
            # Test user creation
            logger.info("Testing user creation...")
            user_service = UserService(db)
            user = await user_service.create_user("test_user_1", "Test User", "test@example.com")
            logger.info(f"Created user: {user}")

            # Test chat session creation
            logger.info("Testing chat session creation...")
            chat_service = ChatService(db)
            session = await chat_service.start_chat("test_user_1")
            logger.info(f"Created session: {session}")

            # Test message addition
            logger.info("Testing message addition...")
            result = await chat_service.add_message(session["session_id"], {
                "role": "user",
                "content": "Hello, this is a test message"
            })
            logger.info(f"Added message: {result}")

            # Commit changes
            db.commit()
            logger.info("Changes committed to database")

        except Exception as e:
            logger.error(f"Error during test: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_database()) 