from typing import List, Dict, Tuple, Set
import torch
from transformers import AutoTokenizer, AutoModel
import re
from Levenshtein import distance
from collections import defaultdict
from .skills_dictionaries import ALL_SKILLS, TECHNICAL_SKILLS, SOFT_SKILLS

class EnhancedSkillExtractor:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Pre-compute embeddings for all skills
        self.skill_embeddings = self._precompute_skill_embeddings()
        
        # Create acronym mappings
        self.acronym_map = self._create_acronym_mappings()
        
        # Proficiency level patterns - made more specific and ordered by precedence
        self.proficiency_patterns = {
            'expert': r'\b(expert|advanced|extensive|strong|proficient)\b',
            'intermediate': r'\b(intermediate|moderate|working|good)\b',
            'beginner': r'\b(basic|beginner|elementary|familiar|exposure)\b'
        }
        
        # Negation patterns
        self.negation_patterns = [
            r'(?:is |are |was |were )?not required\b',
            r'(?:is |are |was |were )?not necessary\b',
            r'no need for\b',
            r'no experience (?:in|with)\b',
            r"don't need\b",
            r'(?:is |are |was |were )?optional\b'
        ]
        
        # Context importance words
        self.context_importance = {
            'high': set(['required', 'must', 'must-have', 'essential', 'critical', 'key', 'core']),
            'medium': set(['preferred', 'desired', 'important', 'should have', 'good to have', 'strong']),
            'low': set(['plus', 'bonus', 'nice to have', 'optional', 'helpful'])
        }

    def _precompute_skill_embeddings(self) -> Dict[str, torch.Tensor]:
        """Pre-compute BERT embeddings for all skills in our dictionary"""
        skill_embeddings = {}
        
        for skill_lower, skill_info in ALL_SKILLS.items():
            skill_name = skill_info['name']
            embedding = self._get_embedding(skill_name)
            skill_embeddings[skill_name] = embedding
            
        return skill_embeddings
    
    def _create_acronym_mappings(self) -> Dict[str, str]:
        """Create mappings between skills and their acronyms"""
        acronym_map = {}
        
        # Common manual mappings
        manual_mappings = {
            'amazon web services': 'AWS',
            'artificial intelligence': 'AI',
            'machine learning': 'ML',
            'natural language processing (nlp)': 'NLP',
            'user interface': 'UI',
            'user experience': 'UX',
            'continuous integration': 'CI',
            'continuous deployment': 'CD',
            'infrastructure as code': 'IaC'
        }
        
        # Add both directions for manual mappings
        for full_form, acronym in manual_mappings.items():
            acronym_map[full_form] = acronym
            acronym_map[acronym.lower()] = full_form
            # Also add the skill name as it appears in ALL_SKILLS
            if full_form in ALL_SKILLS:
                actual_name = ALL_SKILLS[full_form]['name']
                acronym_map[acronym.lower()] = actual_name.lower()
            # Special case for AWS which is in ALL_SKILLS as just "AWS"
            if acronym == "AWS":
                acronym_map[acronym.lower()] = acronym
        
        # Generate acronyms for multi-word skills
        for skill_info in ALL_SKILLS.values():
            name = skill_info['name'].lower()
            if ' ' in name:
                words = name.split()
                acronym = ''.join(word[0].upper() for word in words)
                if len(acronym) >= 2:  # Only add if acronym is 2+ letters
                    acronym_map[name] = acronym
                    acronym_map[acronym.lower()] = name
        
        return acronym_map

    def _get_embedding(self, text: str) -> torch.Tensor:
        """Get BERT embedding for a piece of text"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()
        return embedding

    def _get_fuzzy_matches(self, text: str, max_distance: int = 2) -> List[Tuple[str, float]]:
        """Find fuzzy matches for a text against our skill dictionary"""
        matches = []
        text_lower = text.lower()
        
        # Check exact matches first
        if text_lower in ALL_SKILLS:
            matches.append((ALL_SKILLS[text_lower]['name'], 1.0))
            return matches
            
        # Check acronym matches
        if text_lower in self.acronym_map:
            full_form = self.acronym_map[text_lower]
            # Special case for AWS which is directly in ALL_SKILLS
            if full_form.upper() == "AWS":
                matches.append(("AWS", 0.95))
                return matches
            if full_form in ALL_SKILLS:
                matches.append((ALL_SKILLS[full_form]['name'], 0.95))
                return matches
        
        # Fuzzy matching using Levenshtein distance
        for skill_info in ALL_SKILLS.values():
            name = skill_info['name'].lower()
            dist = distance(text_lower, name)
            if dist <= max_distance:
                confidence = 1.0 - (dist / (max_distance + 1))
                matches.append((skill_info['name'], confidence))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _detect_skill_level(self, context: str, skill_name: str) -> Tuple[str, float]:
        """Detect the skill level from the surrounding context for a specific skill"""
        context_lower = context.lower()
        skill_lower = skill_name.lower()
        
        # Find the skill position in context
        skill_pos = context_lower.find(skill_lower)
        if skill_pos == -1:
            return 'unspecified', 0.5
        
        # Look for level indicators near the skill (before and after)
        before_context = context_lower[:skill_pos]
        after_context = context_lower[skill_pos + len(skill_lower):]
        
        # Check patterns in order of precedence
        for level, pattern in self.proficiency_patterns.items():
            # Look for pattern close to the skill mention
            if re.search(pattern, before_context[-50:]) or re.search(pattern, after_context[:50]):
                confidence_map = {
                    'expert': 1.0,
                    'intermediate': 0.7,
                    'beginner': 0.4
                }
                return level, confidence_map[level]
        
        # Default to unspecified with medium confidence
        return 'unspecified', 0.5

    def _check_negation(self, context: str, phrase: str) -> bool:
        """Check if the skill is mentioned in a negative context"""
        context_lower = context.lower()
        phrase_pos = context_lower.find(phrase.lower())
        
        if phrase_pos == -1:
            return False
            
        # Check only the part before the phrase and a few words after
        pre_context = context_lower[:phrase_pos].strip()
        words_after = ' '.join(context_lower[phrase_pos:].split()[:3])
        check_context = pre_context + ' ' + words_after
        
        return any(re.search(pattern, check_context) for pattern in self.negation_patterns)

    def _calculate_context_importance(self, context: str, skill_name: str) -> float:
        """Calculate importance based on contextual words near the skill"""
        context_lower = context.lower()
        skill_lower = skill_name.lower()
        
        # Find the skill position in context
        skill_pos = context_lower.find(skill_lower)
        if skill_pos == -1:
            return 0.5
        
        # Look for importance indicators in the same sentence/clause as the skill
        # Split by sentence boundaries and find which sentence contains the skill
        sentences = re.split(r'[.!?]', context_lower)
        skill_sentence = None
        
        for sentence in sentences:
            if skill_lower in sentence:
                skill_sentence = sentence.strip()
                break
        
        if not skill_sentence:
            return 0.5
        
        # Check for high importance first
        if any(term in skill_sentence for term in self.context_importance['high']):
            return 1.0
            
        # Check for medium importance 
        if any(term in skill_sentence for term in self.context_importance['medium']):
            return 0.7
            
        # Check for low importance
        if any(term in skill_sentence for term in self.context_importance['low']):
            return 0.4
            
        # Default to medium if no importance indicators found
        return 0.5

    def extract_skills_with_confidence(self, text: str, context_window: int = 100) -> List[Dict]:
        """
        Main method to extract skills with enhanced confidence scoring
        """
        results = []
        text_lower = text.lower()
        
        # First pass: Exact and fuzzy matching
        words = text_lower.split()
        for i in range(len(words)):
            # Check phrases of different lengths
            for length in range(1, min(5, len(words) - i + 1)):
                phrase = ' '.join(words[i:i+length])
                
                # Get fuzzy matches for the phrase
                fuzzy_matches = self._get_fuzzy_matches(phrase)
                
                for skill_name, base_confidence in fuzzy_matches:
                    # Get context around the match
                    start_pos = text_lower.find(phrase)
                    if start_pos != -1:
                        context_start = max(0, start_pos - context_window)
                        context_end = min(len(text), start_pos + len(phrase) + context_window)
                        context = text[context_start:context_end]
                        
                        # Various confidence factors
                        skill_level, level_confidence = self._detect_skill_level(context, skill_name)
                        is_negated = self._check_negation(context, phrase)
                        context_importance = self._calculate_context_importance(context, skill_name)
                        
                        # Skip if negated
                        if is_negated:
                            continue
                        
                        # Calculate final confidence score with adjusted weights
                        # For preferred/optional skills, reduce the final confidence
                        if context_importance <= 0.7:  # Medium or low importance
                            base_confidence *= 0.8  # Reduce base confidence for non-required skills
                        
                        confidence = (
                            base_confidence * 0.5 +    # Base match confidence
                            level_confidence * 0.2 +   # Skill level confidence
                            context_importance * 0.3    # Context importance
                        )
                        
                        # Get skill info
                        skill_info = ALL_SKILLS.get(skill_name.lower(), {'name': skill_name, 'category': 'technical', 'subcategory': 'other'}).copy()
                        
                        # Add enhanced information
                        skill_info.update({
                            'confidence': confidence,
                            'skill_level': skill_level,
                            'context': context,
                            'matched_text': phrase,
                            'base_confidence': base_confidence,
                            'context_importance': context_importance
                        })
                        
                        # Check for duplicates and keep highest confidence
                        existing = next((r for r in results if r['name'].lower() == skill_name.lower()), None)
                        if existing:
                            if confidence > existing['confidence']:
                                results.remove(existing)
                                results.append(skill_info)
                        else:
                            results.append(skill_info)
        
        return results 