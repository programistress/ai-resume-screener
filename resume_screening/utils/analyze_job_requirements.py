from .find_keyword_phrases import find_keyword_phrases
from .bert_keyword_utils import extract_key_requirements

def analyze_job_requirements(job_text):
    important_terms = extract_key_requirements(job_text)
    key_phrases = find_keyword_phrases(job_text, important_terms)
    
    requirements = {
        'important_terms': important_terms,
        'key_phrases': key_phrases
    }
    
    return requirements