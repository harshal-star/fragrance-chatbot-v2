import re
from typing import Dict, List

def extract_scent_preferences(message: str) -> Dict[str, List[str]]:
    """Extract liked and disliked scents from a message."""
    liked = []
    disliked = []
    # Simple rules
    if "like" in message:
        liked += re.findall(r"like[s]? ([a-zA-Z, ]+)", message)
    if "dislike" in message:
        disliked += re.findall(r"dislike[s]? ([a-zA-Z, ]+)", message)
    # Split by 'and' or ','
    liked = [item.strip() for l in liked for item in re.split(r",|and", l)]
    disliked = [item.strip() for l in disliked for item in re.split(r",|and", l)]
    # Remove empty strings
    liked = [s for s in liked if s]
    disliked = [s for s in disliked if s]
    return {"favorite_scents": liked, "disliked_scents": disliked}

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