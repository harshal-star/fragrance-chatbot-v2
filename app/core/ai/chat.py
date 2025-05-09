import logging
import sys
import time
import random
import asyncio
from typing import Dict, List, AsyncGenerator, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.session import get_session, save_session
from app.core.utils import client, get_system_prompt, format_conversation_history, logger

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def generate_response(session: Dict, message: str, db: Session) -> AsyncGenerator[str, None]:
    """Generate a streaming response for the given message using OpenAI API"""
    try:
        # Ensure conversation history has the correct structure
        if not session.get("conversation_history"):
            session["conversation_history"] = {"messages": []}
    
        
        # Format conversation history for OpenAI
        messages = [
            {"role": "system", "content": get_system_prompt()}
        ] + format_conversation_history(session["conversation_history"])

        print(30 * "------------")
        print(messages)
        print(30 * "------------")
        
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
        
        # --- Append the assistant's response only if it's not a duplicate ---
        messages_list = session["conversation_history"]["messages"]
        logger.info(f"Messages list length before append: {len(messages_list)}")
        if not (messages_list and messages_list[-1]["role"] == "assistant" and messages_list[-1]["content"] == full_response):
            logger.info(f"Appending assistant message: {full_response[:50]}...")
            messages_list.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            logger.info("Duplicate assistant message detected, not appending.")
        
        # Save the updated session
        save_session(
            session["session_id"],
            session.get("user_id"),
            session,
            db
        )
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        yield "I apologize, but I'm having trouble processing your request right now. Could you please try again?"