from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Tuple
import torch
from .skills_dictionaries import ALL_SKILLS
import re
from collections import Counter

class JobRequirementsAnalyzer:
    
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        self.skill_embeddings = self._precompute_skill_embeddings()
    
    #precalculate embeddings for every skill in dictionary
    def _precompute_skill_embeddings(self) -> Dict[str, torch.Tensor]:
        print("Pre-computing skill embeddings... (this only happens once)")
        skill_embeddings = {}
        
        #get embeddings for every skill name we have in allskills and store in in dict {skill_embeddings["Python"] = [those 384 numbers]}
        for skill_lower, skill_info in ALL_SKILLS.items():
            skill_name = skill_info['name']
            embedding = self._get_embedding(skill_name)
            skill_embeddings[skill_name] = embedding
            
        return skill_embeddings
    
    #convert text to vectors
    def _get_embedding(self, text: str) -> torch.Tensor:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()
        return embedding #returns just the CLS token that captures meaning of the whole phrase
    
    
    # extracting skills with exact matching and similiarity matching
    def extract_skills_with_similarity(self, job_text: str, similarity_threshold: float = 0.7) -> List[Dict]:
        found_skills = []
        
        # extract exact skills
        exact_matches = self._extract_exact_skills(job_text)
        found_skills.extend(exact_matches)
        
        # split job text into meaningful chunks
        chunks = self._extract_meaningful_chunks(job_text)
        
        for chunk in chunks:
            # skip if we already have exact match, condition : loop
            if any(skill['name'].lower() in chunk.lower() for skill in exact_matches):
                continue
                
            # get embedding for this chunk
            chunk_embedding = self._get_embedding(chunk)
            
            # skill embeddings from init
            for skill_name, skill_embedding in self.skill_embeddings.items():
                # Calculate similarity (cosine similarity)
                similarity = torch.cosine_similarity(chunk_embedding, skill_embedding, dim=0)
                
                if similarity > similarity_threshold: # default 0.7     
                    skill_info = ALL_SKILLS.get(skill_name.lower()) # name, category, subcategory
                    if skill_info and skill_info not in found_skills: # avoiding duplicates
                        found_skills.append({
                            **skill_info,
                            'confidence': float(similarity),
                            'matched_text': chunk
                        })
        
        return found_skills
    
    # extract skills that match our dictionary, get a list of found skills
    def _extract_exact_skills(self, text: str) -> List[Dict]:
        if not text:
            return []
        
        # clean up text
        text_lower = text.lower()
        text_lower = re.sub(r'[^\w\s+#\./-]', ' ', text_lower)
        
        words = text_lower.split()
        phrases = []
        
        # creating all possible word combinations (1, 2, 3, 4 word phrases)
        phrases.extend(words)
        
        for n in range(2, 5):
            for i in range(len(words) - n + 1):
                phrases.append(' '.join(words[i:i+n]))
        
        # matching with skills dictionary 
        found_skills = {}
        for phrase in phrases:
            skill_info = ALL_SKILLS.get(phrase)
            if skill_info:
                skill_name = skill_info['name']
                if skill_name not in found_skills:
                    found_skills[skill_name] = {**skill_info, 'confidence': 1.0}
        
        return list(found_skills.values())
    
    
    def _extract_meaningful_chunks(self, text: str) -> List[str]:
        
        # splitting text by common delimeters
        chunks = re.split(r'[,\n•·▪◦\-\*]|\sand\s|\sor\s', text)
        
        # cleaning and filtering
        meaningful_chunks = []
        for chunk in chunks:
            chunk = chunk.strip() # remove whitespace before or after chunk
            # keep chunks that are 2-5 words 
            word_count = len(chunk.split())
            if 2 <= word_count <= 5 and len(chunk) > 5:
                meaningful_chunks.append(chunk)
        
        return meaningful_chunks
    
    def calculate_skill_importance(self, job_text: str, extracted_skills: List[Dict]) -> List[Dict]:

        # start with empty counter
        skill_counts = Counter()
        text_lower = job_text.lower()
        
        
        # count how many times a skill is mentioned in a job text
        for skill in extracted_skills:
            skill_name = skill['name']
            count = len(re.findall(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower))
            skill_counts[skill_name] = count
        
        # check position importance (skills mentioned early are often more important)
        skill_positions = {}
        for skill in extracted_skills:
            skill_name = skill['name']
            match = re.search(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower) # to find the first mention of the skill position
            if match:
                # count position relevance - higher - earlier in text
                position_score = 1.0 - (match.start() / len(text_lower))
                skill_positions[skill_name] = position_score
        
        # check if skill appears in "required" vs "nice to have" sections
        required_section = self._find_section(text_lower, ['required', 'must have', 'essential', 'mandatory'])
        preferred_section = self._find_section(text_lower, ['preferred', 'nice to have', 'bonus', 'optional'])
        
        # final importance scores with all the factors
        skills_with_importance = []
        for skill in extracted_skills:
            skill_name = skill['name']
            
            # how many times was mentioned (max score - 3)
            count_score = min(skill_counts.get(skill_name, 0) / 3.0, 1.0) 
            # how early in text its mentioned
            position_score = skill_positions.get(skill_name, 0.5)
            #confidence from similarity match 1 for exact match
            confidence_score = skill.get('confidence', 1.0)
            
            # section bonus
            section_multiplier = 1.0
            if required_section and skill_name.lower() in required_section:
                section_multiplier = 1.5
            elif preferred_section and skill_name.lower() in preferred_section:
                section_multiplier = 0.8
            
            # calculate weighted importance
            importance = (
                (count_score * 0.3) +  # How often it's mentioned
                (position_score * 0.2) +  # How early it appears
                (confidence_score * 0.3) +  # How confident we are it's a skill
                (0.2)  # Base score
            ) * section_multiplier
            
            skills_with_importance.append({
                **skill,  # Spread all original skill fields
                'importance': min(importance, 1.0),  # Add calculated importance
                'mention_count': skill_counts.get(skill_name, 0),  # Add count
                'position_score': position_score  # Add position
            })
        
        # Sort by importance
        skills_with_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return skills_with_importance
    
        
    # finding a section in text with wirds that we need and extracting everything after    
    def _find_section(self, text: str, keywords: List[str]) -> str:
        for keyword in keywords:
            pattern = rf'{keyword}.*?(?=\n\n|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        return ""
    
    #CALLS all the other functions and makes the result
    def analyze(self, job_text: str) -> Dict:
        # all skills - exact and similarity
        extracted_skills = self.extract_skills_with_similarity(job_text)
        
        # importance score
        skills_with_importance = self.calculate_skill_importance(job_text, extracted_skills)
        
        # just the technical and just the soft skills
        technical_skills = [s for s in skills_with_importance if s['category'] == 'technical']
        soft_skills = [s for s in skills_with_importance if s['category'] == 'soft']
        
        # non-skill requirement
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
    
    
    # finding important requirements that arent skills
    def _extract_key_phrases(self, text: str) -> List[str]:
        patterns = [
            r'\d+\+?\s*years?\s+(?:of\s+)?experience',
            r'bachelor\'?s?\s+degree|master\'?s?\s+degree|phd|doctorate',
            r'experience\s+with\s+\w+(?:\s+\w+){0,3}',
            r'knowledge\s+of\s+\w+(?:\s+\w+){0,3}',
            r'familiarity\s+with\s+\w+(?:\s+\w+){0,3}',
        ]
        
        # find all matches in text and add them to our list 
        key_phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_phrases.extend(matches)
        
        # removimg duplicates while keeping the original order 
        seen = set()
        unique_phrases = []
        for phrase in key_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower not in seen:
                seen.add(phrase_lower)
                unique_phrases.append(phrase)
        
        return unique_phrases
    
    def analyze_job_requirements_ml(job_text: str) -> Dict:
        analyzer = JobRequirementsAnalyzer()
        return analyzer.analyze(job_text)