from django.db import models
from common.bert_utils import get_bert_embedding

class JobDescription(models.Model):
  raw_text = models.TextField() 
  uploaded_at = models.DateTimeField(auto_now_add=True) # for tracking?
  embedding_vector = models.JSONField(blank=True, null=True)
  
  def __str__(self):
    return self.raw_text[:50]  # first 50 characters of the raw text
    
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    try:
      if self.raw_text:
        self.embedding_vector = get_bert_embedding(self.raw_text)
        super().save(update_fields=['embedding_vector'])
      else:
        print("No text could be embedded.")
    except Exception as e:
      print(f"Error embedding text: {e}")