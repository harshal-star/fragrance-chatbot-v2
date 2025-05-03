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
from app.services.chat_analysis_service import ChatAnalysisService
from app.models.schemas import (
    ChatMessage,
    ChatSession,
    UserCreate,
    ScentPreferencesCreate
)
from app.services.image_analysis import analyze_image
from app.core.ai.chat import generate_response
from app.services.openai_profile_extraction import OpenAIProfileExtraction
from app.core.config import settings, Settings
from fastapi import BackgroundTasks

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class ChatService:
    def __init__(self, db: Session, config: Settings):
        self.config = config
        self.db = db
        self.user_service = UserService(db)
        self.profile_service = ProfileService(db)
        self.openai_extraction = OpenAIProfileExtraction(api_key=config.OPENAI_API_KEY)
        self.analysis_service = ChatAnalysisService(self.profile_service, self.openai_extraction)

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
            print("\n=== Starting Chat ===")
            print(f"User ID: {user_id}")
            
            # Create user if not exists
            if user_id:
                print("Creating user...")
                # Create UserCreate instance
                user_create = UserCreate(user_id=user_id)
                await self.user_service.create_user(user_create)
                print("User created")
            else:
                print("No user_id provided")
            
            session = get_session_by_user(user_id, self.db)
            if not session:
                print("Creating new session...")
                session = create_session(user_id, self.db)
                print(f"New session created: {session}")
            else:
                print(f"Existing session found: {session}")
            
            initial_message = "Hey there! I'm Lila, your personal fragrance consultant. I'd love to help you create a fragrance that perfectly matches your style. Would you like to start by telling me a bit about yourself or sharing a photo of yourself?"
            
            # Add initial message to conversation history
            session["conversation_history"]["messages"].append({
                "role": "assistant",
                "content": initial_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Save session with updated history
            save_session(session["session_id"], session.get("user_id"), session, self.db)
            print(f"Session saved with user_id: {session.get('user_id')}")
            
            return {
                "session_id": session["session_id"],
                "message": initial_message
            }
        except Exception as e:
            print(f"\nError in start_chat: {str(e)}")
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
            print("\n=== Chat Processing ===")
            print(f"Session ID: {session_id}")
            print(f"Message: {message}")
            
            session = get_session(session_id, self.db)
            if not session:
                raise ValueError("Session not found")
            print(f"Session found: {session}")

            # Add user message to history
            session["conversation_history"]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            print("Added user message to session")

            # Process image if provided
            if image_data:
                try:
                    logger.info(f"Starting image analysis for session {session_id}")
                    image_analysis = await analyze_image(image_data)
                    logger.info(f"Image analysis output: {image_analysis!r}")
                    analysis_content = f"Image Analysis: {image_analysis}"
                    session["conversation_history"]["messages"].append({
                        "role": "system",
                        "content": analysis_content,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    logger.info(f"Added image analysis to conversation history for session {session_id}")
                    # Run OpenAI structured extraction on the image analysis output if present and non-empty
                    if session.get("user_id") and image_analysis:
                        try:
                            logger.info(f"Running structured extraction on image analysis for session {session_id}: {analysis_content!r}")
                            await self.analysis_service.analyze_chat_messages(
                                session["user_id"],
                                [{"role": "system", "content": analysis_content}]
                            )
                            logger.info(f"Structured extraction on image analysis completed for session {session_id}")
                        except Exception as e:
                            logger.error(f"Error extracting profile data from image analysis for session {session_id}: {str(e)}")
                    # Save session with updated history
                    save_session(session_id, session.get("user_id"), session, self.db)
                    logger.info(f"Session saved after image analysis for session {session_id}")
                    response_text = image_analysis.get('chat_response') or image_analysis.get('analysis') or str(image_analysis)
                    return {"message": response_text}
                except Exception as e:
                    logger.error(f"Error analyzing image for session {session_id}: {str(e)}")
                    error_message = "I apologize, but I had trouble analyzing your image. Let's continue our conversation about your fragrance preferences."
                    session["conversation_history"]["messages"].append({
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    save_session(session_id, session.get("user_id"), session, self.db)
                    logger.info(f"Session saved after image analysis error for session {session_id}")
                    return {"message": error_message}

            # Analyze chat messages to extract preferences (for text messages)
            if session.get("user_id"):
                print("\nCalling chat analysis service...")
                print(f"User ID: {session['user_id']}")
                print(f"Messages to analyze: {session['conversation_history']['messages']}")
                await self.analysis_service.analyze_chat_messages(
                    session["user_id"],
                    session["conversation_history"]["messages"]
                )
                print("Chat analysis complete")
            else:
                print("\nNo user_id found in session, skipping analysis")

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
            print("Added assistant message to session")

            return {
                "message": full_response,
                "session_id": session_id
            }

        except Exception as e:
            print(f"\nError in process_message: {str(e)}")
            logger.error(f"Error processing message: {str(e)}")
            raise

    async def process_message_stream(
        self,
        session_id: str,
        message: str,
        background_tasks: BackgroundTasks,
        image_data: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream the assistant's response for text chat.
        """
        session = get_session(session_id, self.db)
        if not session:
            yield "data: Error: Session not found\n\n"
            return

        # Add user message to history
        session["conversation_history"]["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Start background analysis (do not await)
        if session.get("user_id"):
            background_tasks.add_task(
                self.analysis_service.analyze_chat_messages,
                session["user_id"],
                session["conversation_history"]["messages"]
            )

        # Truncate conversation history if needed
        session["conversation_history"]["messages"] = truncate_conversation_history(
            session["conversation_history"]["messages"]
        )

        # Stream the assistant's response
        async for chunk in generate_response(session, message, self.db):
            yield f"data: {chunk}\n\n" 