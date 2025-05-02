import re
from typing import Dict, List

def extract_scent_preferences(message: str) -> Dict[str, List[str]]:
    """Extract liked and disliked scents from a message."""
    liked = []
    disliked = []
    
    # Convert message to lowercase for case-insensitive matching
    message = message.lower()
    
    # Define patterns for likes and dislikes
    like_patterns = [
        r"(?:i )?(?:like|love|enjoy|prefer|want|looking for|favorite) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?",
        r"([a-z, ]+)(?: scent| fragrance| smell| perfume)? (?:is|are) (?:nice|good|great|amazing|wonderful|my favorite)",
        r"(?:i )?(?:am|feel) (?:drawn to|attracted to) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?",
        r"(?:i )?(?:would like|want) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?"
    ]
    
    dislike_patterns = [
        r"(?:i )?(?:dislike|hate|don't like|do not like|avoid|not a fan of) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?",
        r"([a-z, ]+)(?: scent| fragrance| smell| perfume)? (?:is|are) (?:bad|terrible|overwhelming|too strong|not for me)",
        r"(?:i )?(?:am|feel) (?:not into|not interested in) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?",
        r"(?:i )?(?:would not|don't want) (?:a |an )?([a-z, ]+)(?: scent| fragrance| smell| perfume)?"
    ]
    
    # Process each pattern
    for pattern in like_patterns:
        matches = re.finditer(pattern, message)
        for match in matches:
            phrase = match.group(1)
            # Split by 'and' or ',' and clean up
            items = [item.strip() for item in re.split(r",|and", phrase)]
            liked.extend(items)
    
    for pattern in dislike_patterns:
        matches = re.finditer(pattern, message)
        for match in matches:
            phrase = match.group(1)
            # Split by 'and' or ',' and clean up
            items = [item.strip() for item in re.split(r",|and", phrase)]
            disliked.extend(items)
    
    # Remove empty strings and duplicates
    liked = list(set(s for s in liked if s))
    disliked = list(set(s for s in disliked if s))
    
    return {
        "favorite_scents": liked,
        "disliked_scents": disliked
    }

def extract_style_preferences(message: str) -> Dict[str, List[str]]:
    """Extract clothing style from a message."""
    style = []
    if "style is" in message:
        found = re.findall(r"style is ([a-zA-Z, ]+)", message)
        style = [item.strip() for l in found for item in re.split(r",|and", l)]
    style = [s for s in style if s]
    return {"clothing_style": style}

# New function for personality traits extraction
def extract_personality_traits(message: str) -> Dict[str, List[str]]:
    """Extract personality traits from a message."""
    # List of common personality traits (expand as needed)
    trait_keywords = [
        "creative", "adventurous", "calm", "outgoing", "introverted", "extroverted", "friendly", "ambitious",
        "thoughtful", "spontaneous", "organized", "curious", "empathetic", "optimistic", "realistic", "playful",
        "serious", "bold", "shy", "confident", "sensitive", "practical", "imaginative", "analytical"
    ]
    found_traits = []
    for trait in trait_keywords:
        # Look for the trait as a whole word (case-insensitive)
        if re.search(rf"\\b{trait}\\b", message, re.IGNORECASE):
            found_traits.append(trait)
    return {"traits": found_traits} 