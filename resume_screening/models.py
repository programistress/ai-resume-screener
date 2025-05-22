from django.db import models
from pathlib import Path
from django.core.exceptions import ValidationError
from .utils.text_extraction import extract_text
from .utils.bert_utils import get_bert_embedding
import os
from .utils.extract_skills import extract_skills_from_text
from .utils.skills_dictionaries import ALL_SKILLS
        

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
                    
                    extracted_skills = extract_skills_from_text(self.extracted_text)
                    self.save_skills(extracted_skills)
                else:
                    print("No text could be extracted.")
            except Exception as e:
                print(f"Error during extraction: {e}")
                
    def save_skills(self, extracted_skills):
        #clear existing skills for this resume to avoid duplicates
        ResumeSkill.objects.filter(resume=self).delete()
        
        for skill_info in extracted_skills:
            #get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            #create the relationship between resume and skill
            ResumeSkill.objects.create(
                resume=self,
                skill=skill,
                confidence=1.0  # default
            )


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
            
    def save_job_skills(self, extracted_skills):
        # clear existing skills for this job to avoid duplicates
        JobSkill.objects.filter(job=self).delete()
        
        for skill_info in extracted_skills:
            # get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            # relationship between job and skill
            JobSkill.objects.create(
                job=self,
                skill=skill,
                importance=1.0  # default
            )
                
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    category = models.CharField(max_length=50, db_index=True)  # 'technical' or 'soft'
    subcategory = models.CharField(max_length=50)  # 'programming_language', 'framework', etc.
    
    def __str__(self):
        return f"{self.name} ({self.category}: {self.subcategory})"
    
    class Meta:
        ordering = ['category', 'subcategory', 'name'],
        indexes = [
            models.Index(fields=['category', 'subcategory']),
        ]

class ResumeSkill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='resumes')
    confidence = models.FloatField(default=1.0)  # Confidence score of skill detection
    
    class Meta:
        unique_together = ('resume', 'skill')

class JobSkill(models.Model):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='jobs')
    importance = models.FloatField(default=1.0)  # Importance of skill for the job
    
    class Meta:
        unique_together = ('job', 'skill')