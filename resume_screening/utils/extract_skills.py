import re
from resume_screening.utils.skills_dictionaries import ALL_SKILLS


def extract_skills_from_text(text):
    """
    extracting skills from text by matching with our skills dictionary
    args: text
    returns: a list of dictionaries
    """
    if not text:
        return []
    
    text_lower = text.lower()
    text_lower = re.sub(r'[^\w\s+#\./-]', ' ', text_lower)
    
    words = text_lower.split()
    phrases = []
    
    # add singular words
    phrases.extend(words)
    
    # add 2-word phrases
    for i in range(len(words) - 1):
        phrases.append(words[i] + ' ' + words[i + 1]) #we subtract 1 because we're going to use both the current index (i) and the next index (i+1) in each iteration
    
    # add 3-word phrases
    for i in range(len(words) - 2):
        phrases.append(words[i] + ' ' + words[i + 1] + ' ' + words[i + 2])
    
    # add 4-word phrases
    for i in range(len(words) - 3):
        phrases.append(words[i] + ' ' + words[i + 1] + ' ' + words[i + 2] + ' ' + words[i + 3])
    
    found_skills = {} #we use a dictionary instead of a list to ensure we don't add duplicate skills.
    for phrase in phrases:
        skill_info = ALL_SKILLS.get(phrase)
        if skill_info:
            skill_name = skill_info['name']
            if skill_name not in found_skills:
                found_skills[skill_name] = skill_info
    
    # convert to list for return
    return list(found_skills.values())
    # output example
    # {
    #     "Python": {"name": "Python", "category": "technical", "subcategory": "programming_languages"},
    #     "Machine Learning": {"name": "Machine Learning", "category": "technical", "subcategory": "data_and_ai"}
    # }
    

def extract_skills_with_context(text, context_window=50):
    """    
    extracts skills with surrounding context for better analysis
    args: text and number of characters before/after to include as context
    returns: list of skills with surrounding context
    """
    
    skills = extract_skills_from_text(text)
    result = []
    
    for skill_info in skills:
        skill_name = skill_info['name']
        pattern = re.compile(re.escape(skill_name), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - context_window)
            end = min(len(text), match.end() + context_window)
            context = text[start:end]

            skill_with_context = skill_info.copy()
            skill_with_context['context'] = context
            skill_with_context['position'] = (match.start(), match.end()) #for interactive ui like highlighting the skill
            result.append(skill_with_context)
    
    return result    
