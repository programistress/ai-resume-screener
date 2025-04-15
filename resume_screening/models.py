from django.db import models
from pathlib import Path
from django.core.exceptions import ValidationError
from .utils.text_extraction import extract_text
from .utils.bert_utils import get_bert_embedding
import os


class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)  # for tracking
    extracted_text = models.TextField(blank=True, null=True)
    embedding_vector = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return self.extracted_text[:50] if self.extracted_text else f"Resume {self.id}"
    
    # validating the file - size, extension
    def clean(self):
        if self.file:
            file_ext = Path(self.file.name).suffix.lower()
            valid_extensions = ['.pdf', '.docx', '.txt']
            
            if file_ext not in valid_extensions:
                raise ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
            
            max_file_size = 10 * 1024 * 1024  # 10 MB
            if self.file.size > max_file_size:
                raise ValidationError(f"File size exceeds maximum limit of {max_file_size / (1024*1024)} MB")
    
    # extracts text, generates embedding vectors
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        file_path = self.file.path
        if os.path.exists(file_path):
            try:
                extracted_text = extract_text(file_path)
                if extracted_text:
                    self.extracted_text = extracted_text 
                    super().save(update_fields=['extracted_text'])
                    self.embedding_vector = get_bert_embedding(self.extracted_text)
                    super().save(update_fields=['embedding_vector'])
                else:
                    print("No text could be extracted.")
            except Exception as e:
                print(f"Error during extraction: {e}")


class JobDescription(models.Model):
    raw_text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    embedding_vector = models.JSONField(blank=True, null=True)
    
    # relationship to Resume model (ForeignKey - one resume to many job desc)
    resume = models.ForeignKey(
        Resume, 
        related_name='job_descriptions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.raw_text[:50]  # first 50 characters of the raw text
    
    # generating bert embeddings for job description text
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