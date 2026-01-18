"""
Enhanced NLP Utils - Now uses advanced NLP when available
"""
from typing import List

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords using advanced NLP if available, fallback to simple
    """
    # Try advanced NLP first
    try:
        from .advanced_nlp import AdvancedNLP
        nlp = AdvancedNLP()
        return nlp.extract_interests(text)
    except:
        # Fallback to simple keyword matching
        return _simple_keyword_extraction(text)


def _simple_keyword_extraction(text: str) -> List[str]:
    """
    Simple keyword extraction based on predefined interests
    (Legacy fallback method)
    """
    text_lower = text.lower()
    
    interest_keywords = {
        'culture': ['culture', 'temple', 'heritage', 'ancient', 'history', 'historical'],
        'history': ['history', 'historical', 'ancient', 'heritage', 'monument'],
        'beach': ['beach', 'coast', 'sea', 'ocean', 'sand', 'swim'],
        'wildlife': ['wildlife', 'whale', 'safari', 'animals', 'nature', 'elephant'],
        'nature': ['nature', 'mountain', 'forest', 'scenic', 'green', 'landscape'],
        'hiking': ['hiking', 'trek', 'walk', 'hike', 'trail', 'climb'],
        'relax': ['relax', 'leisure', 'peaceful', 'calm', 'rest', 'spa'],
        'adventure': ['adventure', 'thrill', 'exciting', 'extreme', 'activity']
    }
    
    detected_interests = []
    for interest, keywords in interest_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_interests.append(interest)
            
    return detected_interests if detected_interests else ['culture', 'nature']

