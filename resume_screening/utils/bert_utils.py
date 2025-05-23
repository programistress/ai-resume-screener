from transformers import AutoModel, AutoTokenizer
import torch

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME) # converts text into tokens the model can understand
    model = AutoModel.from_pretrained(MODEL_NAME) # the neural network that processes these tokens
except Exception as e:
    print(f"Error loading model: {e}")
    # Provide fallback
    tokenizer = None
    model = None
    
#convert text to bert embedding vector 
def get_bert_embedding(text):
    tokens = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        output = model(**tokens)
    embedding = output.last_hidden_state[:, 0, :].squeeze().tolist()  # CLS token representation
    return embedding
