from typing import List, Dict, Optional
from datetime import datetime
import re
from app.models.schemas import (
    UserProfileCreate, ScentPreferencesCreate,
    StylePreferencesCreate, PersonalityTraitsCreate
)
from app.services.profile_service import ProfileService
from app.core.utils import logger

class ChatAnalysisService:
    def __init__(self, profile_service: ProfileService):
        self.profile_service = profile_service
        self.scent_keywords = {
            "floral": ["flower", "rose", "jasmine", "lily", "floral"],
            "woody": ["wood", "cedar", "sandalwood", "oak", "moss"],
            "citrus": ["citrus", "lemon", "orange", "grapefruit", "bergamot"],
            "spicy": ["spice", "cinnamon", "pepper", "ginger", "clove"],
            "fresh": ["fresh", "clean", "crisp", "light", "air"],
            "sweet": ["sweet", "vanilla", "honey", "sugar", "caramel"],
            "intense": ["strong", "intense", "powerful", "bold", "rich"],
            "light": ["light", "subtle", "soft", "delicate", "mild"]
        }
        self.style_keywords = {
            "casual": ["casual", "relaxed", "comfortable", "everyday"],
            "formal": ["formal", "elegant", "sophisticated", "business"],
            "sporty": ["sporty", "athletic", "active", "outdoor"],
            "bohemian": ["bohemian", "boho", "hippie", "artistic"],
            "minimalist": ["minimal", "simple", "clean", "modern"],
            "vintage": ["vintage", "retro", "classic", "old-school"]
        }
        self.color_keywords = [
            "black", "white", "red", "blue", "green", "yellow", "purple",
            "pink", "orange", "brown", "gray", "navy", "beige", "gold", "silver"
        ]

    async def analyze_chat_messages(self, user_id: str, messages: List[Dict[str, str]]) -> None:
        """
        Analyze chat messages to extract user preferences and personality traits
        """
        try:
            # Extract personality traits
            personality_traits = await self._extract_personality_traits(messages)
            if personality_traits:
                await self._update_personality_traits(user_id, personality_traits)

            # Extract scent preferences
            scent_preferences = await self._extract_scent_preferences(messages)
            if scent_preferences:
                await self._update_scent_preferences(user_id, scent_preferences)

            # Extract style preferences
            style_preferences = await self._extract_style_preferences(messages)
            if style_preferences:
                await self._update_style_preferences(user_id, style_preferences)

            # Update user profile based on extracted information
            await self._update_user_profile(user_id, personality_traits, scent_preferences, style_preferences)

        except Exception as e:
            logger.error(f"Error analyzing chat messages: {str(e)}")
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

        user_messages = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
        
        # Extract liked and disliked scents
        favorite_scents = []
        disliked_scents = []
        preferred_families = []
        intensity_preference = "medium"

        # Look for scent-related keywords
        for family, keywords in self.scent_keywords.items():
            if family in ["intense", "light"]:
                if any(keyword in user_messages.lower() for keyword in keywords):
                    intensity_preference = family
            else:
                if any(keyword in user_messages.lower() for keyword in keywords):
                    preferred_families.append(family)

        # Look for explicit mentions of likes/dislikes
        for msg in messages:
            if msg["role"] == "user":
                content = msg["content"].lower()
                if "like" in content or "love" in content:
                    for family in self.scent_keywords:
                        if family in content:
                            favorite_scents.append(family)
                elif "dislike" in content or "hate" in content:
                    for family in self.scent_keywords:
                        if family in content:
                            disliked_scents.append(family)

        return {
            "favorite_scents": list(set(favorite_scents)),
            "disliked_scents": list(set(disliked_scents)),
            "preferred_fragrance_families": list(set(preferred_families)),
            "intensity_preference": intensity_preference
        }

    async def _extract_style_preferences(self, messages: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Extract style preferences from chat messages
        """
        if not messages:
            return None

        user_messages = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
        
        # Extract style preferences
        clothing_style = None
        color_preferences = []
        fashion_brands = []
        accessories_preferences = []

        # Determine clothing style
        for style, keywords in self.style_keywords.items():
            if any(keyword in user_messages.lower() for keyword in keywords):
                clothing_style = style
                break

        # Extract color preferences
        for color in self.color_keywords:
            if color in user_messages.lower():
                color_preferences.append(color)

        # Look for brand mentions (simple implementation)
        brand_pattern = r"(gucci|prada|chanel|louis vuitton|dior|versace|ralph lauren|calvin klein|hugo boss|armani)"
        brand_matches = re.findall(brand_pattern, user_messages.lower())
        fashion_brands = list(set(brand_matches))

        # Look for accessory mentions
        accessory_keywords = ["bag", "watch", "jewelry", "sunglasses", "hat", "scarf", "belt"]
        for keyword in accessory_keywords:
            if keyword in user_messages.lower():
                accessories_preferences.append(keyword)

        return {
            "clothing_style": clothing_style,
            "color_preferences": color_preferences,
            "fashion_brands": fashion_brands,
            "accessories_preferences": accessories_preferences
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
        existing_traits = self.profile_service.get_personality_traits(user_id)
        if existing_traits:
            self.profile_service.update_personality_traits(user_id, traits)
        else:
            traits_create = PersonalityTraitsCreate(
                user_id=user_id,
                traits=traits.get("traits", []),
                confidence_score=traits.get("confidence_score", 0.0)
            )
            self.profile_service.create_personality_traits(traits_create)

    async def _update_scent_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Update scent preferences in the database
        """
        existing_preferences = self.profile_service.get_scent_preferences(user_id)
        if existing_preferences:
            self.profile_service.update_scent_preferences(user_id, preferences)
        else:
            preferences_create = ScentPreferencesCreate(
                user_id=user_id,
                favorite_scents=preferences.get("favorite_scents", []),
                disliked_scents=preferences.get("disliked_scents", []),
                preferred_fragrance_families=preferences.get("preferred_fragrance_families", []),
                intensity_preference=preferences.get("intensity_preference", "medium")
            )
            self.profile_service.create_scent_preferences(preferences_create)

    async def _update_style_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Update style preferences in the database
        """
        existing_preferences = self.profile_service.get_style_preferences(user_id)
        if existing_preferences:
            self.profile_service.update_style_preferences(user_id, preferences)
        else:
            preferences_create = StylePreferencesCreate(
                user_id=user_id,
                clothing_style=preferences.get("clothing_style", ""),
                color_preferences=preferences.get("color_preferences", []),
                fashion_brands=preferences.get("fashion_brands", []),
                accessories_preferences=preferences.get("accessories_preferences", [])
            )
            self.profile_service.create_style_preferences(preferences_create)

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