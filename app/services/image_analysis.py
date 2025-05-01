from typing import Dict, Optional
from app.core.ai.llm import LLMService
from app.core.config import settings
from app.core.utils import logger

async def analyze_image(image_data: str) -> Dict:
    """Analyze an image using the LLM service."""
    try:
        # Initialize LLM service with config
        llm_service = LLMService(settings)
        
        # Analyze the image
        result = await llm_service.analyze_image(image_data)
        print(30 * "----------")
        print("IMAGE ANALYSIS RESULT: ", result)
        print(30 * "----------")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise 