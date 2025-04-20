def find_keyword_phrases(job_text, important_terms, max_phrase_length=3):
    # lowercase
    job_text_lower = job_text.lower()
    lowercased_terms = [term.lower() for term in important_terms]

    # simple tokenization by splitting on whitespace
    words = job_text_lower.split()
    
    # find phrases containing important terms
    phrases = []
    for i in range(len(words)):
        # check phrases of different lengths
        for length in range(1, min(max_phrase_length + 1, len(words) - i + 1)):
            phrase = ' '.join(words[i:i+length])
            
            # check if phrase contains any important term
            if any(term in phrase for term in lowercased_terms):
                # make sure the phrase doesn't end with a stopword
                last_word = words[i+length-1]
                stopwords = {'the', 'and', 'a', 'to', 'of', 'in', 'for'}
                if last_word not in stopwords:
                    phrases.append(phrase)
    
    # remove duplicates and sort by length (longer phrases first)
    unique_phrases = list(set(phrases))
    unique_phrases.sort(key=len, reverse=True)
    
    # remove phrases that are substrings of others
    final_phrases = []
    for phrase in unique_phrases:
        if not any(phrase in other_phrase and phrase != other_phrase for other_phrase in unique_phrases):
            final_phrases.append(phrase)
    
    return final_phrases[:20]  # return top 20 phrases