"""
Reasoning Engine - Multi-step logical reasoning for the agent
Analyzes user intent and makes inferences
"""
from typing import Dict, List, Any
from collections import deque


class ReasoningEngine:
    """
    Provides multi-step reasoning capabilities
    - Intent analysis
    - Inference from context
    - Goal decomposition
    - Constraint satisfaction
    """
    
    def __init__(self):
        self.reasoning_rules = self._load_reasoning_rules()
    
    def _load_reasoning_rules(self) -> Dict:
        """
        Load reasoning rules for inference
        """
        return {
            'honeymoon': {
                'inferred_interests': ['beach', 'romantic', 'relax', 'luxury'],
                'inferred_constraints': {'pace': 'relaxed', 'accommodation_level': 'luxury'},
                'avoid': ['hiking', 'adventure']
            },
            'family_trip': {
                'inferred_interests': ['family', 'culture', 'beach', 'nature'],
                'inferred_constraints': {'pace': 'moderate', 'group_size': 'family'},
                'prefer': ['kid-friendly activities']
            },
            'adventure': {
                'inferred_interests': ['adventure', 'hiking', 'wildlife', 'nature'],
                'inferred_constraints': {'pace': 'intensive', 'accommodation_level': 'budget'},
                'prefer': ['outdoor activities']
            },
            'cultural_tour': {
                'inferred_interests': ['culture', 'history', 'nature'],
                'inferred_constraints': {'pace': 'moderate'},
                'prefer': ['temples', 'museums', 'heritage sites']
            },
            'beach_vacation': {
                'inferred_interests': ['beach', 'relax', 'water sports', 'food'],
                'inferred_constraints': {'pace': 'relaxed'},
                'prefer': ['coastal locations']
            },
            'backpacking': {
                'inferred_interests': ['adventure', 'budget', 'culture', 'hiking'],
                'inferred_constraints': {'pace': 'flexible', 'accommodation_level': 'budget'},
                'prefer': ['local experiences', 'public transport']
            }
        }
    
    def analyze_intent(self, text: str, memory: deque) -> Dict:
        """
        Analyze user intent with multi-step reasoning
        """
        intent = {
            'primary_goal': self._identify_primary_goal(text),
            'constraints': [],
            'preferences': [],
            'implicit_needs': []
        }
        
        # Apply reasoning rules
        if intent['primary_goal'] in self.reasoning_rules:
            rules = self.reasoning_rules[intent['primary_goal']]
            
            # Add inferred interests
            intent['preferences'].extend(
                {'type': 'interest', 'value': i} 
                for i in rules.get('inferred_interests', [])
            )
            
            # Add inferred constraints
            for key, value in rules.get('inferred_constraints', {}).items():
                intent['constraints'].append({
                    'type': key,
                    'value': value,
                    'inferred': True
                })
            
            # Add implicit needs
            intent['implicit_needs'] = rules.get('prefer', [])
        
        # Context-based reasoning from memory
        if memory:
            context_insights = self._reason_from_context(memory)
            intent['implicit_needs'].extend(context_insights)
        
        return intent
    
    def _identify_primary_goal(self, text: str) -> str:
        """
        Identify primary goal from text
        """
        text_lower = text.lower()
        
        goal_patterns = {
            'honeymoon': ['honeymoon', 'newlywed', 'just married', 'romantic getaway'],
            'family_trip': ['family', 'kids', 'children', 'family vacation'],
            'adventure': ['adventure', 'adrenaline', 'extreme', 'thrill'],
            'cultural_tour': ['cultural', 'heritage', 'history', 'temples'],
            'beach_vacation': ['beach', 'seaside', 'coastal', 'ocean'],
            'backpacking': ['backpack', 'budget travel', 'hostel', 'low-cost']
        }
        
        for goal, patterns in goal_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return goal
        
        return 'general_tourism'
    
    def _reason_from_context(self, memory: deque) -> List[str]:
        """
        Make inferences from conversation history
        """
        insights = []
        
        # Look at past interactions
        for interaction in memory:
            if interaction['type'] == 'plan_generated':
                # User has planned before - might want variety
                insights.append('prefer_new_destinations')
            
            elif interaction['type'] == 'feedback_received':
                feedback = interaction['data'].get('feedback', {})
                rating = interaction['data'].get('rating', 0)
                
                # Learn from past feedback
                if rating >= 4:
                    insights.append('repeat_successful_pattern')
                elif rating <= 2:
                    insights.append('avoid_similar_pattern')
        
        return insights
    
    def reason_about_constraints(self, goals: Dict) -> Dict:
        """
        Reason about constraint compatibility and conflicts
        """
        issues = []
        suggestions = []
        
        budget = goals.get('budget', 0)
        days = goals.get('days', 0)
        interests = goals.get('interests', [])
        
        # Budget-days reasoning
        min_daily_cost = 100  # Minimum viable daily cost
        if budget > 0 and days > 0:
            daily_budget = budget / days
            if daily_budget < min_daily_cost:
                issues.append('budget_too_low')
                suggestions.append({
                    'issue': 'Low daily budget',
                    'suggestion': f'Consider increasing budget or reducing days',
                    'reason': f'Daily budget of ${daily_budget:.0f} is quite tight'
                })
        
        # Interest-days compatibility
        if 'luxury' in interests and budget / days < 200:
            issues.append('luxury_budget_mismatch')
            suggestions.append({
                'issue': 'Luxury interest with limited budget',
                'suggestion': 'Consider standard accommodation or increase budget',
                'reason': 'Luxury experiences typically cost $200+ per day'
            })
        
        # Adventure-days reasoning
        if 'adventure' in interests and days < 3:
            suggestions.append({
                'issue': 'Short duration for adventure',
                'suggestion': 'Consider adding 1-2 days for better adventure experiences',
                'reason': 'Adventure activities are best enjoyed over 3+ days'
            })
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'feasible': len(issues) == 0
        }
    
    def explain_reasoning(self, decision: Dict) -> str:
        """
        Generate human-readable explanation of reasoning process
        """
        explanation = "Here's my reasoning: "
        
        primary_goal = decision.get('primary_goal', 'general tour')
        explanation += f"You're planning a {primary_goal}. "
        
        if decision.get('implicit_needs'):
            needs = decision['implicit_needs'][:3]
            explanation += f"Based on this, you probably need {', '.join(needs)}. "
        
        inferred = [c for c in decision.get('constraints', []) if c.get('inferred')]
        if inferred:
            explanation += f"I also inferred {len(inferred)} additional preferences from your request. "
        
        return explanation
