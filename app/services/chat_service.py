from typing import List, Dict, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.database import DBChatHistory
from app.services.chat_analysis_service import ChatAnalysisService
from app.services.profile_service import ProfileService
from app.core.utils import logger
from app.core.config import settings
import openai

class ChatService:
    def __init__(self, profile_service: ProfileService):
        self.profile_service = profile_service
        self.analysis_service = ChatAnalysisService(profile_service)
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def process_message(self, user_id: str, message: str, db: Session) -> str:
        """
        Process a chat message and generate a response
        """
        try:
            # Get chat history
            chat_history = await self.get_chat_history(user_id, db)

            # Add the new message to chat history
            new_message = DBChatHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                role="user",
                content=message,
                timestamp=datetime.utcnow()
            )
            db.add(new_message)
            db.commit()

            # Analyze chat messages to extract user preferences
            await self.analysis_service.analyze_chat_messages(user_id, chat_history)

            # Get user profile and preferences
            user_profile = self.profile_service.get_user_profile(user_id)
            scent_preferences = self.profile_service.get_scent_preferences(user_id)
            style_preferences = self.profile_service.get_style_preferences(user_id)
            personality_traits = self.profile_service.get_personality_traits(user_id)

            # Generate response using LLM
            response = await self._generate_llm_response(
                message,
                chat_history,
                user_profile,
                scent_preferences,
                style_preferences,
                personality_traits
            )

            # Add the response to chat history
            response_message = DBChatHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                role="assistant",
                content=response,
                timestamp=datetime.utcnow()
            )
            db.add(response_message)
            db.commit()

            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    async def get_chat_history(self, user_id: str, db: Session) -> List[Dict[str, str]]:
        """
        Get chat history for a user
        """
        chat_history = db.query(DBChatHistory).filter(
            DBChatHistory.user_id == user_id
        ).order_by(DBChatHistory.timestamp).all()

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in chat_history
        ]

    async def clear_chat_history(self, user_id: str, db: Session) -> None:
        """
        Clear chat history for a user
        """
        db.query(DBChatHistory).filter(DBChatHistory.user_id == user_id).delete()
        db.commit()

    async def _generate_llm_response(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_profile: Optional[Dict],
        scent_preferences: Optional[Dict],
        style_preferences: Optional[Dict],
        personality_traits: Optional[Dict]
    ) -> str:
        """
        Generate a response using the LLM
        """
        try:
            # Prepare system message with user context
            system_message = self._prepare_system_message(
                user_profile,
                scent_preferences,
                style_preferences,
                personality_traits
            )

            # Prepare messages for the LLM
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # Add chat history
            for msg in chat_history[-10:]:  # Limit to last 10 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call the LLM
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."

    def _prepare_system_message(
        self,
        user_profile: Optional[Dict],
        scent_preferences: Optional[Dict],
        style_preferences: Optional[Dict],
        personality_traits: Optional[Dict]
    ) -> str:
        """
        Prepare system message with user context
        """
        context_parts = []

        if user_profile:
            context_parts.append(f"User's style preference: {user_profile.get('style_preference', 'unknown')}")
            context_parts.append(f"User's vibe: {user_profile.get('vibe', 'unknown')}")

        if scent_preferences:
            favorite_scents = ", ".join(scent_preferences.get("favorite_scents", []))
            disliked_scents = ", ".join(scent_preferences.get("disliked_scents", []))
            preferred_families = ", ".join(scent_preferences.get("preferred_fragrance_families", []))
            context_parts.append(f"User's scent preferences: Likes {favorite_scents}, Dislikes {disliked_scents}")
            context_parts.append(f"Preferred fragrance families: {preferred_families}")
            context_parts.append(f"Intensity preference: {scent_preferences.get('intensity_preference', 'medium')}")

        if style_preferences:
            context_parts.append(f"Clothing style: {style_preferences.get('clothing_style', 'unknown')}")
            context_parts.append(f"Color preferences: {', '.join(style_preferences.get('color_preferences', []))}")
            context_parts.append(f"Fashion brands: {', '.join(style_preferences.get('fashion_brands', []))}")

        if personality_traits:
            context_parts.append(f"Personality traits: {', '.join(personality_traits.get('traits', []))}")
            context_parts.append(f"Primary trait: {personality_traits.get('primary_trait', 'unknown')}")

        system_message = "You are a fragrance expert and personal stylist. "
        if context_parts:
            system_message += "Here's what I know about the user:\n" + "\n".join(context_parts)
        system_message += "\n\nPlease provide personalized fragrance recommendations and style advice based on this information."

        return system_message 