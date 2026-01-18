"""
Advanced NLP with Semantic Understanding
Uses sentence transformers for semantic similarity
"""
from typing import List, Dict
import re


class AdvancedNLP:
    """
    Advanced NLP that goes beyond keyword matching
    Uses semantic understanding
    """
    
    def __init__(self):
        self.embedder = None
        self._try_load_embedder()
        
        # Expanded interest taxonomy
        self.interest_taxonomy = {
            'culture': {
                'keywords': ['culture', 'temple', 'heritage', 'ancient', 'history', 'historical', 
                           'traditional', 'museum', 'monument', 'religious', 'buddhist', 'spiritual'],
                'semantic': ['cultural experience', 'traditional ceremonies', 'local customs',
                           'historical sites', 'sacred places']
            },
            'beach': {
                'keywords': ['beach', 'coast', 'sea', 'ocean', 'sand', 'swim', 'snorkel',
                           'diving', 'surfing', 'water sports', 'marine'],
                'semantic': ['coastal relaxation', 'water activities', 'seaside vacation',
                           'tropical paradise', 'beach resort']
            },
            'wildlife': {
                'keywords': ['wildlife', 'whale', 'safari', 'animals', 'nature', 'elephant',
                           'leopard', 'birds', 'turtle', 'monkey', 'national park'],
                'semantic': ['animal encounters', 'safari adventure', 'wildlife watching',
                           'nature preserve', 'endangered species']
            },
            'nature': {
                'keywords': ['nature', 'mountain', 'forest', 'scenic', 'green', 'landscape',
                           'waterfall', 'lake', 'river', 'jungle', 'rainforest'],
                'semantic': ['natural beauty', 'scenic landscapes', 'wilderness exploration',
                           'ecological tourism', 'pristine environments']
            },
            'hiking': {
                'keywords': ['hiking', 'trek', 'walk', 'hike', 'trail', 'climb', 'trekking',
                           'mountain climbing', 'peak', 'summit'],
                'semantic': ['trekking adventure', 'mountain trails', 'hiking expedition',
                           'outdoor activities', 'peak climbing']
            },
            'adventure': {
                'keywords': ['adventure', 'thrill', 'exciting', 'extreme', 'activity',
                           'adrenaline', 'zip line', 'rafting', 'camping', 'paragliding'],
                'semantic': ['thrilling experiences', 'extreme sports', 'adventure tourism',
                           'adrenaline rush', 'outdoor excitement']
            },
            'relax': {
                'keywords': ['relax', 'leisure', 'peaceful', 'calm', 'rest', 'spa',
                           'massage', 'wellness', 'yoga', 'meditation', 'tranquil'],
                'semantic': ['peaceful retreat', 'wellness tourism', 'relaxation therapy',
                           'stress relief', 'serene environment']
            },
            'food': {
                'keywords': ['food', 'cuisine', 'restaurant', 'eat', 'dining', 'culinary',
                           'cooking', 'local food', 'street food', 'gourmet'],
                'semantic': ['culinary experience', 'local cuisine', 'food tourism',
                           'gastronomic journey', 'traditional dishes']
            },
            'luxury': {
                'keywords': ['luxury', 'premium', 'upscale', 'high-end', 'exclusive',
                           'VIP', 'private', 'boutique', '5-star', 'deluxe'],
                'semantic': ['luxury experience', 'premium service', 'exclusive access',
                           'high-end accommodation', 'VIP treatment']
            },
            'budget': {
                'keywords': ['budget', 'affordable', 'cheap', 'economical', 'backpack',
                           'low-cost', 'value', 'budget-friendly'],
                'semantic': ['budget travel', 'economical options', 'affordable tourism',
                           'backpacker friendly', 'value for money']
            },
            'romantic': {
                'keywords': ['romantic', 'honeymoon', 'couple', 'anniversary', 'love',
                           'intimate', 'romantic getaway', 'couples retreat'],
                'semantic': ['romantic escape', 'couples vacation', 'honeymoon destination',
                           'intimate moments', 'love celebration']
            },
            'family': {
                'keywords': ['family', 'kids', 'children', 'family-friendly', 'parents',
                           'family vacation', 'child-friendly'],
                'semantic': ['family activities', 'kid-friendly', 'multi-generational',
                           'family bonding', 'children activities']
            }
        }
    
    def _try_load_embedder(self):
        """Try to load sentence transformer, fallback gracefully"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded semantic embedding model")
        except:
            print("⚠️ Using keyword-based NLP (install sentence-transformers for semantic understanding)")
            self.embedder = None
    
    def extract_interests(self, text: str) -> List[str]:
        """
        Extract interests using both keyword and semantic matching
        """
        if not text:
            return ['culture', 'nature']
        
        text_lower = text.lower()
        detected = set()
        
        # Keyword-based detection (fast)
        for interest, taxonomy in self.interest_taxonomy.items():
            if any(kw in text_lower for kw in taxonomy['keywords']):
                detected.add(interest)
        
        # Semantic matching if available (more accurate)
        if self.embedder and len(text) > 20:
            semantic_matches = self._semantic_match(text)
            detected.update(semantic_matches)
        
        return list(detected) if detected else ['culture', 'nature']
    
    def _semantic_match(self, text: str, threshold: float = 0.5) -> List[str]:
        """
        Use semantic similarity to match user intent
        """
        try:
            text_embedding = self.embedder.encode([text])[0]
            matches = []
            
            for interest, taxonomy in self.interest_taxonomy.items():
                # Embed semantic phrases
                semantic_phrases = taxonomy['semantic']
                phrase_embeddings = self.embedder.encode(semantic_phrases)
                
                # Calculate similarity
                from numpy import dot
                from numpy.linalg import norm
                
                for phrase_emb in phrase_embeddings:
                    similarity = dot(text_embedding, phrase_emb) / (
                        norm(text_embedding) * norm(phrase_emb)
                    )
                    
                    if similarity > threshold:
                        matches.append(interest)
                        break
            
            return matches
        except:
            return []
    
    def extract_constraints(self, text: str) -> Dict:
        """
        Extract implicit constraints from text
        """
        constraints = {
            'time_preference': None,
            'pace': None,
            'accommodation_level': None,
            'group_size': None
        }
        
        text_lower = text.lower()
        
        # Time preferences
        if any(word in text_lower for word in ['morning', 'early', 'sunrise', 'dawn']):
            constraints['time_preference'] = 'morning'
        elif any(word in text_lower for word in ['evening', 'sunset', 'night', 'late']):
            constraints['time_preference'] = 'evening'
        
        # Pace
        if any(word in text_lower for word in ['relaxed', 'slow', 'leisure', 'easy-going', 'chill']):
            constraints['pace'] = 'relaxed'
        elif any(word in text_lower for word in ['fast', 'packed', 'busy', 'intensive', 'action']):
            constraints['pace'] = 'intensive'
        else:
            constraints['pace'] = 'moderate'
        
        # Accommodation level
        if any(word in text_lower for word in ['luxury', '5-star', 'upscale', 'premium']):
            constraints['accommodation_level'] = 'luxury'
        elif any(word in text_lower for word in ['budget', 'hostel', 'cheap', 'economical']):
            constraints['accommodation_level'] = 'budget'
        else:
            constraints['accommodation_level'] = 'standard'
        
        # Group size
        if any(word in text_lower for word in ['solo', 'alone', 'myself', 'individual']):
            constraints['group_size'] = 'solo'
        elif any(word in text_lower for word in ['couple', 'two', 'partner', 'romantic']):
            constraints['group_size'] = 'couple'
        elif any(word in text_lower for word in ['family', 'kids', 'children']):
            constraints['group_size'] = 'family'
        elif any(word in text_lower for word in ['group', 'friends', 'together']):
            constraints['group_size'] = 'group'
        
        return constraints
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis
        """
        positive_words = ['love', 'amazing', 'wonderful', 'great', 'beautiful', 'perfect',
                         'excited', 'enjoy', 'fantastic', 'excellent']
        negative_words = ['avoid', 'not', 'dont', "don't", 'dislike', 'hate', 'boring',
                         'bad', 'terrible', 'worst']
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'


# Update main extract_keywords function
def extract_keywords(text: str) -> List[str]:
    """
    Enhanced keyword extraction with semantic understanding
    """
    nlp = AdvancedNLP()
    return nlp.extract_interests(text)


def analyze_user_text(text: str) -> Dict:
    """
    Comprehensive text analysis
    Returns interests, constraints, and sentiment
    """
    nlp = AdvancedNLP()
    return {
        'interests': nlp.extract_interests(text),
        'constraints': nlp.extract_constraints(text),
        'sentiment': nlp.analyze_sentiment(text)
    }
