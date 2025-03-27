from django.db import models
from pathlib import Path
from django.core.exceptions import ValidationError
from .utils.text_extraction import extract_text
import os


class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True) # for tracking
    extracted_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.extracted_text[:50] if self.extracted_text else f"Resume {self.id}"
    
    def clean(self):
        if self.file:
            file_ext = Path(self.file.name).suffix.lower()
            valid_extensions = ['.pdf', '.docx', '.txt']
            
            if file_ext not in valid_extensions:
                raise ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")

            max_file_size = 10 * 1024 * 1024  # 10 MB
            if self.file.size > max_file_size:
                raise ValidationError(f"File size exceeds maximum limit of {max_file_size / (1024*1024)} MB")
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        file_path = self.file.path  
        if os.path.exists(file_path):
            try:
                extracted_text = extract_text(file_path)
                if extracted_text:
                    self.extracted_text = extracted_text
                    super().save(update_fields=['extracted_text'])
                else:
                    print("No text could be extracted.")
            except Exception as e:
                print(f"Error during extraction: {e}")
        
      