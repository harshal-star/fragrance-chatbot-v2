import logging
import time
import random
import asyncio
from typing import Dict, List, AsyncGenerator
from datetime import datetime
from app.models.schemas import SessionContext
from app.services.session import get_session, update_session
from app.core.utils import client, get_system_prompt, format_conversation_history

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_response(session: SessionContext, message: str) -> AsyncGenerator[str, None]:
    """Generate a streaming response for the given message using OpenAI API"""
    # Add user message to conversation history
    session.conversation_history.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Format conversation history for OpenAI
        messages = [
            {"role": "system", "content": get_system_prompt()}
        ] + format_conversation_history(session.conversation_history)
        
        # Call OpenAI API with streaming
        stream = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # Use the correct model name
            messages=messages,
            stream=True,
            temperature=0.8,
            max_tokens=500
        )
        logger.info("Successfully received streaming response from OpenAI")
        
        # Stream the response with natural typing delay
        logger.debug("Starting to stream response")
        full_response = ""
        buffer = ""
        last_yield_time = time.time()
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                buffer += content
                current_time = time.time()
                
                # Add natural typing delay and yield in chunks
                if len(buffer) >= 3 or current_time - last_yield_time >= 0.1:
                    delay = random.uniform(0.05, 0.15)
                    await asyncio.sleep(delay)
                    
                    yield buffer
                    full_response += buffer
                    buffer = ""
                    last_yield_time = current_time
        
        # Yield any remaining content
        if buffer:
            yield buffer
            full_response += buffer
        
        # Add bot response to conversation history
        session.conversation_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update session
        session.last_interaction = datetime.now().isoformat()
        update_session(session)
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        yield "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

async def process_chat_message(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """Process a chat message and return a streaming response"""
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")
    
    async for response_chunk in generate_response(session, message):
        yield response_chunk 