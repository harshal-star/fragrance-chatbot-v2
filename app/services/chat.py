import sys
import logging
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.session import create_session, get_session, get_session_by_user, save_session
from app.services.user import UserService
from app.core.utils import logger, truncate_conversation_history
from app.services.profile_extraction import (
    extract_scent_preferences,
    extract_style_preferences,
    extract_personality_traits
)
from app.services.profile_service import ProfileService
from app.models.schemas import ChatMessage, ChatSession
from app.services.image_analysis import analyze_image
from app.core.ai.chat import generate_response

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def get_session(self, session_id: str, db: Session) -> Optional[Dict]:
        """Get a session by ID."""
        try:
            return get_session(session_id, db)
        except Exception as e:
            logger.error(f"Error getting session: {str(e)}")
            return None

    async def start_chat(self, user_id: str) -> Dict:
        """Start a new chat session for a user."""
        try:
            session = get_session_by_user(user_id, self.db)
            if not session:
                session = create_session(user_id, self.db)
            
            initial_message = "Hey there! I'm Lila, your personal fragrance consultant. I'd love to help you create a fragrance that perfectly matches your style. Would you like to start by telling me a bit about yourself or sharing a photo of yourself?"
            
            # Add initial message to conversation history
            session["conversation_history"]["messages"].append({
                "role": "assistant",
                "content": initial_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Save session with updated history
            save_session(session["session_id"], session.get("user_id"), session, self.db)
            
            return {
                "session_id": session["session_id"],
                "message": initial_message
            }
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            raise

    async def generate_response(self, session: Dict, message: str, db: Session) -> AsyncGenerator[str, None]:
        """Generate a streaming response for the given message."""
        try:
            async for chunk in generate_response(session, message, db):
                yield chunk
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

    async def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session."""
        try:
            session = get_session(session_id, self.db)
            if not session:
                raise ValueError("Session not found")
            return session["conversation_history"]["messages"]
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            raise

    async def add_message(self, session_id: str, message: Dict) -> bool:
        """Add a message to the chat history."""
        try:
            session = get_session(session_id, self.db)
            if not session:
                return False

            # Ensure conversation history exists
            if not session.get("conversation_history"):
                session["conversation_history"] = {"messages": []}

            # Add the new message with timestamp
            session["conversation_history"]["messages"].append({
                "role": message["role"],
                "content": message["content"],
                "timestamp": datetime.utcnow().isoformat()
            })

            # Save the updated session
            save_session(
                session_id,
                session.get("user_id"),
                session,
                self.db
            )

            return True
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise

    async def get_user_chat(self, user_id: str) -> Optional[Dict]:
        """Get the active chat session for a user."""
        try:
            session = get_session_by_user(user_id, self.db)
            if not session:
                return None
            
            # Ensure conversation history exists and has the correct structure
            if not session.get("conversation_history"):
                session["conversation_history"] = {"messages": []}
                save_session(
                    session["session_id"],
                    session.get("user_id"),
                    session,
                    self.db
                )
            
            return session
        except Exception as e:
            logger.error(f"Error getting user chat: {str(e)}")
            raise

    async def process_message(self, session_id: str, message: str, image_data: Optional[str] = None) -> Dict:
        """Process a chat message and optionally an image."""
        try:
            # Get session
            session = get_session(session_id, self.db)
            if not session:
                raise ValueError("Session not found")

            # Add user message to history
            session["conversation_history"]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # If image is provided, analyze it
            if image_data:
                print("IMAGE DATA FOUND!!")
                try:
                    # Analyze the image
                    image_analysis = await analyze_image(image_data)
                    
                    # Add image analysis to conversation history
                    session["conversation_history"]["messages"].append({
                        "role": "assistant",
                        "content": image_analysis["chat_response"],
                        "image_analysis": image_analysis["analysis"],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Save session with updated history
                    save_session(session_id, session.get("user_id"), session, self.db)
                    
                    return {
                        "message": image_analysis["chat_response"],
                        "analysis": image_analysis["analysis"]
                    }
                except Exception as e:
                    logger.error(f"Error analyzing image: {str(e)}")
                    error_message = "I apologize, but I had trouble analyzing your image. Let's continue our conversation about your fragrance preferences."
                    session["conversation_history"]["messages"].append({
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Save session with updated history
                    save_session(session_id, session.get("user_id"), session, self.db)
                    return {"message": error_message}

            # Process regular message
            # Truncate conversation history if needed
            session["conversation_history"]["messages"] = truncate_conversation_history(
                session["conversation_history"]["messages"]
            )
            
            response_generator = generate_response(session, message, self.db)
            full_response = ""
            async for chunk in response_generator:
                full_response += chunk

            # Add assistant's response to history
            session["conversation_history"]["messages"].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Save session with updated history
            save_session(session_id, session.get("user_id"), session, self.db)

            return {
                "message": full_response,
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise 