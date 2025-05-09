import os
import logging
from logging.handlers import RotatingFileHandler
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import tiktoken
from typing import List, Dict

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read system prompt from file
with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Read image analysis prompt from file
with open("prompts/image_analysis_prompt.txt", "r", encoding="utf-8") as f:
    IMAGE_EXTRACTION_PROMPT = f.read()

# Configure logging
def setup_logging():
    """Configure logging with both file and console handlers"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

def get_system_prompt() -> str:
    """Get the system prompt for the chatbot"""
    return SYSTEM_PROMPT

def get_image_analysis_prompt() -> str:
    """Get the image analysis prompt for the chatbot"""
    return IMAGE_EXTRACTION_PROMPT

def format_conversation_history(history: dict) -> list:
    """Format conversation history for OpenAI API"""
    formatted_history = []
    for message in history.get("messages", []):
        formatted_history.append({
            "role": message["role"],
            "content": message["content"]
        })
    return formatted_history

def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error estimating tokens: {str(e)}")
        # Fallback: roughly estimate 1 token per 4 characters
        return len(text) // 4

def truncate_conversation_history(history: List[Dict], max_tokens: int = 6000) -> List[Dict]:
    """
    Truncate conversation history to stay within token limit.
    Keeps the most recent messages while staying under the token limit.
    """
    try:
        total_tokens = 0
        truncated_history = []
        
        # Process messages in reverse order (most recent first)
        for message in reversed(history):
            message_tokens = estimate_tokens(message.get("content", ""))
            
            # If adding this message would exceed the limit, stop
            if total_tokens + message_tokens > max_tokens:
                break
                
            total_tokens += message_tokens
            truncated_history.insert(0, message)  # Insert at beginning to maintain order
            
        return truncated_history
    except Exception as e:
        logger.error(f"Error truncating conversation history: {str(e)}")
        # Return empty history if there's an error
        return [] 