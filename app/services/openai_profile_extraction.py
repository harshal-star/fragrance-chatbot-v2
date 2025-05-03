import json
from typing import Dict, List
from app.core.config import settings
from app.core.utils import logger
import openai

class OpenAIProfileExtraction:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    async def extract_profile_data(self, message: str) -> Dict:
        """
        Extract user profile information using OpenAI's structured output.
        """
        try:
            print("\n=== OpenAI Extraction ===")
            print(f"Input message: {message}")
            
            prompt = f"""
            Extract user preferences and traits from the following message. 
            Return the information in a structured JSON format.
            
            Message: {message}
            
            Extract the following information:
            1. Scent Preferences:
               - Favorite scents (list of specific scents or fragrance families)
               - Disliked scents (list of specific scents or fragrance families)
               - Intensity preference (light/medium/intense)
            
            2. Style Preferences:
               - Primary clothing style
               - All mentioned styles
            
            3. Personality Traits:
               - List of detected personality traits
               - Primary trait (most prominent)
               - Confidence scores for each trait
            
            Return the data in this exact JSON format:
            {{
                "scent_preferences": {{
                    "favorite_scents": [],
                    "disliked_scents": [],
                    "preferred_fragrance_families": [],
                    "intensity_preference": "medium"
                }},
                "style_preferences": {{
                    "clothing_style": null,
                    "all_styles": []
                }},
                "personality_traits": {{
                    "traits": [],
                    "primary_trait": null,
                    "confidence_score": {{}}
                }}
            }}
            """
            
            print("\nSending request to OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a profile extraction assistant. Extract user preferences and traits from messages."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            print("\nReceived response from OpenAI")
            print(f"Response type: {type(response)}")
            print(f"Response content: {response.choices[0].message.content}")
            
            # Parse the response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Validate and clean the data
            cleaned_data = self._clean_extracted_data(extracted_data)
            print("\nCleaned data:")
            print(json.dumps(cleaned_data, indent=2))
            
            return cleaned_data
            
        except Exception as e:
            print(f"\nError in OpenAI extraction: {str(e)}")
            logger.error(f"Error extracting profile data: {str(e)}")
            return self._get_default_profile_data()

    def _clean_extracted_data(self, data: Dict) -> Dict:
        """Clean and validate the extracted data"""
        # Ensure all required fields exist
        if "scent_preferences" not in data:
            data["scent_preferences"] = self._get_default_scent_preferences()
        if "style_preferences" not in data:
            data["style_preferences"] = self._get_default_style_preferences()
        if "personality_traits" not in data:
            data["personality_traits"] = self._get_default_personality_traits()
            
        # Clean scent preferences
        scent_prefs = data["scent_preferences"]
        scent_prefs["favorite_scents"] = [(s or "").lower().strip() for s in scent_prefs.get("favorite_scents", [])]
        scent_prefs["disliked_scents"] = [(s or "").lower().strip() for s in scent_prefs.get("disliked_scents", [])]
        scent_prefs["preferred_fragrance_families"] = [(f or "").lower().strip() for f in scent_prefs.get("preferred_fragrance_families", [])]
        scent_prefs["intensity_preference"] = (scent_prefs.get("intensity_preference") or "medium").lower()
        
        # Clean style preferences
        style_prefs = data["style_preferences"]
        style_prefs["clothing_style"] = (style_prefs.get("clothing_style") or "").lower().strip() or None
        style_prefs["all_styles"] = [(s or "").lower().strip() for s in style_prefs.get("all_styles", [])]
        
        # Clean personality traits
        personality = data["personality_traits"]
        personality["traits"] = [(t or "").lower().strip() for t in personality.get("traits", [])]
        personality["primary_trait"] = (personality.get("primary_trait") or "").lower().strip() or None
        personality["confidence_score"] = personality.get("confidence_score", {})
        
        return data

    def _get_default_profile_data(self) -> Dict:
        """Return default profile data structure"""
        return {
            "scent_preferences": self._get_default_scent_preferences(),
            "style_preferences": self._get_default_style_preferences(),
            "personality_traits": self._get_default_personality_traits()
        }

    def _get_default_scent_preferences(self) -> Dict:
        return {
            "favorite_scents": [],
            "disliked_scents": [],
            "preferred_fragrance_families": [],
            "intensity_preference": "medium"
        }

    def _get_default_style_preferences(self) -> Dict:
        return {
            "clothing_style": None,
            "all_styles": []
        }

    def _get_default_personality_traits(self) -> Dict:
        return {
            "traits": [],
            "primary_trait": None,
            "confidence_score": {}
        } 