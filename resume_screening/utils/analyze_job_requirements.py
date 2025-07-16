from typing import List, Dict, Tuple
import torch
from .enhanced_skill_extraction import EnhancedSkillExtractor
import re
from collections import Counter

class JobRequirementsAnalyzer:
    def __init__(self):
        self.skill_extractor = EnhancedSkillExtractor()
    
    def analyze(self, job_text: str) -> Dict:
        """
        Analyze job requirements using enhanced skill extraction
        
        Args:
            job_text: The job description text to analyze
            
        Returns:
            Dictionary containing analyzed requirements
        """
        # Extract skills with enhanced confidence scoring
        extracted_skills = self.skill_extractor.extract_skills_with_confidence(job_text)
        
        # Calculate importance scores
        skills_with_importance = self.calculate_skill_importance(job_text, extracted_skills)
        
        # Separate technical and soft skills
        technical_skills = [s for s in skills_with_importance if s['category'] == 'technical']
        soft_skills = [s for s in skills_with_importance if s['category'] == 'soft']
        
        # Extract non-skill requirements
        key_phrases = self._extract_key_phrases(job_text)
        
        return {
            'all_skills': skills_with_importance,
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'key_phrases': key_phrases,
            'skill_summary': {
                'total_skills_found': len(skills_with_importance),
                'technical_count': len(technical_skills),
                'soft_count': len(soft_skills),
                'top_skills': skills_with_importance[:10]  # top 10 most important skills
            }
        }
    
    def calculate_skill_importance(self, job_text: str, extracted_skills: List[Dict]) -> List[Dict]:
        """Calculate final importance scores for extracted skills"""
        skill_counts = Counter()
        text_lower = job_text.lower()
        
        # Count skill mentions
        for skill in extracted_skills:
            skill_name = skill['name']
            count = len(re.findall(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower))
            skill_counts[skill_name] = count
        
        # Calculate position scores
        skill_positions = {}
        for skill in extracted_skills:
            skill_name = skill['name']
            match = re.search(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower)
            if match:
                position_score = 1.0 - (match.start() / len(text_lower))
                skill_positions[skill_name] = position_score
        
        # Find required/preferred sections
        required_section = self._find_section(text_lower, ['required', 'must have', 'essential', 'mandatory'])
        preferred_section = self._find_section(text_lower, ['preferred', 'nice to have', 'bonus', 'optional'])
        
        # Calculate final importance scores
        skills_with_importance = []
        for skill in extracted_skills:
            skill_name = skill['name']
            
            # Mention count score (max score - 3)
            count_score = min(skill_counts.get(skill_name, 0) / 3.0, 1.0)
            
            # Position score
            position_score = skill_positions.get(skill_name, 0.5)
            
            # Get confidence and context importance from enhanced extraction
            confidence_score = skill.get('confidence', 1.0)
            context_importance = skill.get('context_importance', 0.5)
            
            # Section multiplier
            section_multiplier = 1.0
            if required_section and skill_name.lower() in required_section:
                section_multiplier = 1.5
            elif preferred_section and skill_name.lower() in preferred_section:
                section_multiplier = 0.8
            
            # Calculate weighted importance
            importance = (
                (count_score * 0.2) +          # How often it's mentioned
                (position_score * 0.2) +       # How early it appears
                (confidence_score * 0.3) +     # How confident we are it's a skill
                (context_importance * 0.3)     # Importance from context
            ) * section_multiplier
            
            # Add all information to result
            skill_info = {
                **skill,  # Include all enhanced extraction info
                'importance': min(importance, 1.0),
                'mention_count': skill_counts.get(skill_name, 0),
                'position_score': position_score
            }
            
            skills_with_importance.append(skill_info)
        
        # Sort by importance
        skills_with_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return skills_with_importance
    
    def _find_section(self, text: str, keywords: List[str]) -> str:
        """Find a section in text based on keywords"""
        for keyword in keywords:
            pattern = rf'{keyword}.*?(?=\n\n|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        return ""
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract important non-skill requirements"""
        patterns = [
            r'\d+\+?\s*years?\s+(?:of\s+)?experience',
            r'bachelor\'?s?\s+degree|master\'?s?\s+degree|phd|doctorate',
            r'experience\s+with\s+\w+(?:\s+\w+){0,3}',
            r'knowledge\s+of\s+\w+(?:\s+\w+){0,3}',
            r'familiarity\s+with\s+\w+(?:\s+\w+){0,3}',
        ]
        
        key_phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_phrases.extend(matches)
        
        # Remove duplicates while keeping order
        seen = set()
        unique_phrases = []
        for phrase in key_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower not in seen:
                seen.add(phrase_lower)
                unique_phrases.append(phrase)
        
        return unique_phrases