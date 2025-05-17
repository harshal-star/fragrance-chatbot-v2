from typing import List, Dict, Optional
from datetime import datetime
from app.models.schemas import (
    UserProfileCreate, ScentPreferencesCreate,
    StylePreferencesCreate, PersonalityTraitsCreate
)
from app.services.profile_service import ProfileService
from app.services.openai_profile_extraction import OpenAIProfileExtraction
from app.core.utils import logger
import json

class ChatAnalysisService:
    def __init__(self, profile_service: ProfileService, openai_extraction: OpenAIProfileExtraction):
        self.profile_service = profile_service
        self.openai_extraction = openai_extraction
        self.message_buffer = []  # Store recent messages
        self.buffer_size = 5      # Number of messages to collect before extraction
        self.trigger_phrases = [
            "like", "love", "prefer", "favorite", "dislike", "hate",
            "style", "fashion", "wear", "dress", "outfit",
            "personality", "trait", "character", "nature"
        ]

    async def analyze_chat_messages(self, user_id: str, messages: List[Dict]) -> None:
        """Analyze chat messages to extract user profile information"""
        try:
            # logger.info(f"Structured extraction input for user {user_id}: {messages}")
            # Combine all user messages into a single string
            combined_message = " ".join([msg["content"] for msg in messages if msg["role"] in ["user", "system"]])
            logger.info(f"Combined message for extraction: {combined_message}")
            logger.info("Calling OpenAI extraction...")
            extracted_data = await self.openai_extraction.extract_profile_data(combined_message)
            # logger.info(f"Structured extraction result for user {user_id}: {extracted_data}")
            await self._process_extracted_data(user_id, extracted_data)
        except Exception as e:
            logger.error(f"Error analyzing chat messages: {str(e)}")
            # Do not raise, just log

    def _should_extract_profile(self) -> bool:
        """Determine if we should extract profile information"""
        # Check buffer size
        if len(self.message_buffer) >= self.buffer_size:
            print("Extracting due to buffer size")
            return True
            
        # Check for trigger phrases in the last message
        if self.message_buffer:
            last_message = self.message_buffer[-1]["content"].lower()
            print(f"\nChecking last message: {last_message}")
            for phrase in self.trigger_phrases:
                if phrase in last_message:
                    print(f"Found trigger phrase: {phrase}")
                    return True
                
        return False

    async def _process_extracted_data(self, user_id: str, extracted_data: Dict) -> None:
        """
        Process and save extracted profile data
        """
        try:
            logger.info(f"Processing extracted data for user {user_id}: {extracted_data}")
            # Process scent preferences
            if extracted_data["scent_preferences"]:
                scent_prefs = extracted_data["scent_preferences"]
                scent_prefs_create = ScentPreferencesCreate(
                    user_id=user_id,
                    favorite_scents=scent_prefs["favorite_scents"],
                    disliked_scents=scent_prefs["disliked_scents"],
                    preferred_fragrance_families=scent_prefs["preferred_fragrance_families"],
                    intensity_preference=scent_prefs["intensity_preference"]
                )
                await self.profile_service.create_scent_preferences(scent_prefs_create)
                logger.info(f"Saved scent preferences for user {user_id}: {scent_prefs_create}")
            
            # Process style preferences
            if extracted_data["style_preferences"]:
                style_prefs = extracted_data["style_preferences"]
                style_prefs_create = StylePreferencesCreate(
                    user_id=user_id,
                    clothing_style=style_prefs["clothing_style"],
                    all_styles=style_prefs["all_styles"]
                )
                await self.profile_service.create_style_preferences(style_prefs_create)
                logger.info(f"Saved style preferences for user {user_id}: {style_prefs_create}")
            
            # Process personality traits
            if extracted_data["personality_traits"]:
                personality = extracted_data["personality_traits"]
                traits_create = PersonalityTraitsCreate(
                    user_id=user_id,
                    traits=personality["traits"],
                    primary_trait=personality["primary_trait"],
                    confidence_score=personality["confidence_score"]
                )
                await self.profile_service.create_personality_traits(user_id, traits_create)
                logger.info(f"Saved personality traits for user {user_id}: {traits_create}")

        except Exception as e:
            logger.error(f"Error processing extracted data: {str(e)}")
            raise

    async def _extract_personality_traits(self, messages: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Extract personality traits from chat messages
        """
        if not messages:
            return None

        # Combine all user messages
        user_messages = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
        
        # Analyze language patterns
        traits = {
            "extroverted": self._count_keywords(user_messages, ["I", "we", "us", "our", "let's", "together"]),
            "introverted": self._count_keywords(user_messages, ["me", "myself", "alone", "quiet", "peaceful"]),
            "analytical": self._count_keywords(user_messages, ["because", "reason", "logic", "analyze", "think"]),
            "emotional": self._count_keywords(user_messages, ["feel", "love", "hate", "happy", "sad", "excited"]),
            "adventurous": self._count_keywords(user_messages, ["new", "try", "explore", "adventure", "discover"]),
            "cautious": self._count_keywords(user_messages, ["careful", "safe", "risk", "maybe", "think about"])
        }

        # Determine primary trait
        primary_trait = max(traits.items(), key=lambda x: x[1])[0]
        
        return {
            "traits": [trait for trait, count in traits.items() if count > 0],
            "primary_trait": primary_trait,
            "confidence_score": self._calculate_confidence_score(traits)
        }

    async def _extract_scent_preferences(self, messages: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Extract scent preferences from chat messages
        """
        if not messages:
            return None

        # Combine all user messages
        user_messages = " ".join([msg["content"].lower() for msg in messages if msg["role"] == "user"])
        
        favorite_scents = []
        disliked_scents = []
        preferred_families = []
        intensity_preference = "medium"

        # Look for explicit mentions of likes/dislikes
        like_patterns = [
            r"(?:i )?(?:like|love|enjoy|prefer|want|looking for) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell)?",
            r"([a-z, ]+)(?: scent| fragrance| smell)? (?:is|are) (?:nice|good|great|amazing|wonderful)"
        ]
        dislike_patterns = [
            r"(?:i )?(?:dislike|hate|don't like|do not like|avoid) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell)?",
            r"([a-z, ]+)(?: scent| fragrance| smell)? (?:is|are) (?:bad|terrible|overwhelming|too strong)"
        ]

        # Process each scent family
        for family, keywords in self.scent_keywords.items():
            if family in ["intense", "light"]:
                # Check intensity preference
                if any(keyword in user_messages for keyword in keywords):
                    intensity_preference = family
                continue

            # Check if any keywords for this family appear in like/dislike contexts
            for pattern in like_patterns:
                matches = re.finditer(pattern, user_messages)
                for match in matches:
                    phrase = match.group(1)
                    if any(keyword in phrase for keyword in keywords):
                        favorite_scents.append(family)
                        preferred_families.append(family)

            for pattern in dislike_patterns:
                matches = re.finditer(pattern, user_messages)
                for match in matches:
                    phrase = match.group(1)
                    if any(keyword in phrase for keyword in keywords):
                        disliked_scents.append(family)

        # Remove duplicates
        favorite_scents = list(set(favorite_scents))
        disliked_scents = list(set(disliked_scents))
        preferred_families = list(set(preferred_families))

        if not (favorite_scents or disliked_scents or preferred_families):
            return None

        return {
            "favorite_scents": favorite_scents,
            "disliked_scents": disliked_scents,
            "preferred_fragrance_families": preferred_families,
            "intensity_preference": intensity_preference
        }

    async def _extract_style_preferences(self, messages: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Extract style preferences from chat messages
        """
        if not messages:
            return None

        user_messages = " ".join([msg["content"].lower() for msg in messages if msg["role"] == "user"])
        
        clothing_styles = []
        
        # Look for style mentions
        for style, keywords in self.style_keywords.items():
            if any(keyword in user_messages for keyword in keywords):
                clothing_styles.append(style)

        if not clothing_styles:
            return None

        return {
            "clothing_style": clothing_styles[0] if clothing_styles else None,  # Use first found style
            "all_styles": clothing_styles
        }

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in text"""
        return sum(text.lower().count(keyword.lower()) for keyword in keywords)

    def _calculate_confidence_score(self, traits: Dict[str, int]) -> float:
        """Calculate confidence score based on trait counts"""
        total_count = sum(traits.values())
        if total_count == 0:
            return 0.0
        return sum(count / total_count for count in traits.values()) / len(traits)

    async def _update_personality_traits(self, user_id: str, traits: Dict) -> None:
        """
        Update personality traits in the database
        """
        try:
            existing_traits = await self.profile_service.get_personality_traits(user_id)
            if existing_traits:
                await self.profile_service.update_personality_traits(user_id, traits)
            else:
                # Create PersonalityTraitsCreate instance
                traits_create = PersonalityTraitsCreate(
                    user_id=user_id,
                    traits=traits.get("traits", []),
                    primary_trait=traits.get("primary_trait"),
                    confidence_score=traits.get("confidence_score", {})
                )
                await self.profile_service.create_personality_traits(user_id, traits_create)
        except Exception as e:
            logger.error(f"Error updating personality traits: {str(e)}")
            raise

    async def _update_scent_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Update scent preferences in the database
        """
        try:
            # Create ScentPreferencesCreate instance
            prefs_create = ScentPreferencesCreate(
                user_id=user_id,
                favorite_scents=preferences.get("favorite_scents", []),
                disliked_scents=preferences.get("disliked_scents", []),
                preferred_fragrance_families=preferences.get("preferred_fragrance_families", []),
                intensity_preference=preferences.get("intensity_preference", "medium")
            )

            # Try to create new preferences
            await self.profile_service.create_scent_preferences(prefs_create)
            
        except Exception as e:
            logger.error(f"Error updating scent preferences: {str(e)}")
            raise

    async def _update_style_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Update style preferences in the database
        """
        try:
            # Create StylePreferencesCreate instance
            prefs_create = StylePreferencesCreate(
                user_id=user_id,
                clothing_style=preferences.get("clothing_style"),
                all_styles=preferences.get("all_styles", [])
            )

            # Try to create new preferences
            await self.profile_service.create_style_preferences(prefs_create)
            
        except Exception as e:
            logger.error(f"Error updating style preferences: {str(e)}")
            raise

    async def _update_user_profile(self, user_id: str, personality_traits: Optional[Dict],
                                 scent_preferences: Optional[Dict], style_preferences: Optional[Dict]) -> None:
        """
        Update user profile based on extracted information
        """
        profile_data = {}
        
        if personality_traits:
            profile_data["personality_type"] = personality_traits.get("primary_trait", "")
        
        if style_preferences:
            profile_data["style_preference"] = style_preferences.get("clothing_style", "")
            profile_data["vibe"] = self._determine_vibe(style_preferences)
        
        if profile_data:
            self.profile_service.update_user_profile(user_id, profile_data)

    def _determine_vibe(self, style_preferences: Dict) -> str:
        """
        Determine the user's vibe based on style preferences
        """
        # TODO: Implement vibe determination logic
        # This could involve analyzing:
        # 1. Color preferences
        # 2. Style choices
        # 3. Brand preferences
        # 4. Accessory choices
        return "casual"  # Default value 