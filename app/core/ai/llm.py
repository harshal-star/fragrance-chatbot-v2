from typing import Dict, Any, AsyncGenerator
import logging
from app.core.config import settings, Settings
import io
from pathlib import Path
import base64
from PIL import Image
import json
from openai import OpenAI, AsyncOpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

# Image analysis prompts
IMAGE_EXTRACTION_PROMPT = """
Analyze this image of a person and provide insights about their:
1. Style and fashion preferences
2. Personality traits (based on appearance and style)
3. Color preferences
4. Overall aesthetic

You have to extract all the details present in the image and provide a detailed analysis of the image.
Once you provide the analysis of the image, ask a relevant followup question to the user either based on the image or based on the user's profile.
"""

class LLMService:
    def __init__(self, config: Settings):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    def _encode_image(self, img, file_identifier):
        buffer = io.BytesIO()
        file_extension = Path(file_identifier).suffix.lower()
        if file_extension in ['.jpg', '.jpeg']:
            img = img.convert('RGB')
            img_format = 'PNG'
        else:
            img_format = 'PNG'
        img.save(buffer, format=img_format)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

    async def _make_openai_call(self, base64_image):
        """Make API call to OpenAI Vision model."""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": IMAGE_EXTRACTION_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        },
                    },
                ],
            }
        ]

        params = {
            "seed": 25,
            "stream": False,  # Changed to False to get complete response at once
            "messages": messages,
            "model": "gpt-4o-mini-2024-07-18",  # Using the vision model directly
            "timeout": 60,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            response = await self.client.chat.completions.create(**params)
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return ""
        except Exception as e:
            logger.error(f"Error making OpenAI call: {str(e)}")
            raise

    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze an image and extract style and personality information."""
        try:
            # Create a temporary directory if it doesn't exist
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            # Generate a unique filename
            file_identifier = temp_dir / f"uploaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Decode base64 and save the image
            image_bytes = base64.b64decode(image_data)
            with open(file_identifier, "wb") as f:
                f.write(image_bytes)
            
            # Open the image using PIL
            with Image.open(file_identifier) as img:
                base64_image = self._encode_image(img, file_identifier)
            
            # Get analysis from OpenAI
            analysis_text = await self._make_openai_call(base64_image)
            
            # Create a natural language response
            chat_response = f"I've analyzed your image, and I'm excited to share what I see! {analysis_text} Let's use these insights to create a fragrance that truly reflects your unique style and personality. Would you like to tell me more about yourself?"
            
            # Clean up the temporary file
            file_identifier.unlink()
            
            return {
                "analysis": analysis_text,
                "chat_response": chat_response
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise

    def _generate_chat_response(self, analysis: Dict[str, Any]) -> str:
        """Generate a natural language response from the analysis."""
        style = analysis["style_analysis"]
        personality = analysis["personality_traits"]
        fragrance = analysis["fragrance_recommendations"]
        
        response = (
            f"Based on your style and appearance, I can see you have a {style['fashion_style']} fashion sense "
            f"with a preference for {', '.join(style['color_preferences'])} colors. "
            f"Your overall aesthetic is {style['aesthetic']}. "
            f"\n\n"
            f"You seem to have {', '.join(personality)} personality traits, which is wonderful! "
            f"\n\n"
            f"Based on this, I would recommend fragrances with {', '.join(fragrance['scent_families'])} notes, "
            f"particularly featuring {', '.join(fragrance['notes'])}. "
            f"A {fragrance['intensity']} intensity would suit you perfectly. "
            f"\n\n"
            f"Would you like me to suggest some specific fragrances that match this profile?"
        )
        
        return response