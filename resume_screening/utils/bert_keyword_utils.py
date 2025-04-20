import torch
from .bert_utils import tokenizer, model

def extract_key_requirements(job_text, top_n = 20):
    # tokenize the job description
    inputs = tokenizer(job_text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # getting model's outputs including attention values
    with torch.no_grad(): # disables gradient calculation because we're not training a model
        outputs = model(**inputs, output_attentions=True)

    # extracting and processing the attention values, average across all attention heads
    attention = outputs.attentions[-1][0].mean(dim=0)
 
    # how much attention each token receives 
    token_attention = attention.sum(dim=0)

    # map attention scores to tokens
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    print("Tokens:")
    print(tokens)

    # create list of (token, attention_score) pairs
    # filter out special tokens and subword tokens
    token_importance = []
    for i, token in enumerate(tokens):
        # Skip special tokens and subword tokens
        if token in ['[CLS]', '[SEP]', '[PAD]'] or token.startswith('##'):
            continue
        
        token_importance.append((token, float(token_attention[i])))
    
    # sort by importance score
    token_importance.sort(key=lambda x: x[1], reverse=True)
    
    # merge subwords and filter common words
    common_words = {'the', 'and', 'a', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'from', 
                   'by', 'as', 'an', 'is', 'are', 'be', 'will', 'or', 'that', 'this'}
    
    important_terms = []
    for token, score in token_importance:
        # skip very short tokens and common words
        if len(token) <= 2 or token.lower() in common_words:
            continue
        
        important_terms.append(token)
        
        # stop once we have enough terms
        if len(important_terms) >= top_n:
            break
    
    return important_terms