from django.db import models
from pathlib import Path
from django.core.exceptions import ValidationError
from .utils.text_extraction import extract_text
from .utils.bert_utils import get_bert_embedding
import os
from .utils.extract_skills import extract_skills_from_text
from .utils.enhanced_skill_extraction import EnhancedSkillExtractor
from .utils.analyze_job_requirements import JobRequirementsAnalyzer
        

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
                    
                    # Use enhanced skill extraction
                    extractor = EnhancedSkillExtractor()
                    enhanced_skills = extractor.extract_skills_with_confidence(self.extracted_text)
                    self.save_enhanced_skills(enhanced_skills)
                else:
                    print("No text could be extracted.")
            except Exception as e:
                print(f"Error during extraction: {e}")
                
    def save_enhanced_skills(self, enhanced_skills):
        """Save skills with enhanced AI analysis data"""
        # Clear existing skills for this resume to avoid duplicates
        ResumeSkill.objects.filter(resume=self).delete()
        
        for skill_info in enhanced_skills:
            # Get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            # Create the relationship between resume and skill with enhanced data
            ResumeSkill.objects.create(
                resume=self,
                skill=skill,
                confidence=skill_info.get('confidence', 1.0),
                skill_level=skill_info.get('skill_level', 'unspecified'),
                matched_text=skill_info.get('matched_text', '')[:200],  # Truncate to field length
                context=skill_info.get('context', '')[:500],  # Truncate context
                base_confidence=skill_info.get('base_confidence', 1.0),
                context_importance=skill_info.get('context_importance', 0.5)
            )
    
    def save_skills(self, extracted_skills):
        """Backward compatibility method for basic skill extraction"""
        # Clear existing skills for this resume to avoid duplicates
        ResumeSkill.objects.filter(resume=self).delete()
        
        for skill_info in extracted_skills:
            # Get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            # Create the relationship between resume and skill
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
                # Use enhanced job requirements analyzer
                analyzer = JobRequirementsAnalyzer()
                job_analysis = analyzer.analyze(self.raw_text)
                self.save_enhanced_job_skills(job_analysis['all_skills'])
            else:
                print("No text could be embedded.")
        except Exception as e:
            print(f"Error embedding text: {e}")
            
    def save_enhanced_job_skills(self, analyzed_skills):
        """Save job skills with enhanced AI analysis data"""
        # Clear existing skills for this job to avoid duplicates
        JobSkill.objects.filter(job=self).delete()
        
        for skill_info in analyzed_skills:
            # Get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            # Create relationship between job and skill with enhanced data
            JobSkill.objects.create(
                job=self,
                skill=skill,
                importance=skill_info.get('importance', 1.0),
                skill_level=skill_info.get('skill_level', 'unspecified'),
                matched_text=skill_info.get('matched_text', '')[:200],  # Truncate to field length
                context=skill_info.get('context', '')[:500],  # Truncate context
                mention_count=skill_info.get('mention_count', 1),
                position_score=skill_info.get('position_score', 0.5),
                confidence=skill_info.get('confidence', 1.0),
                context_importance=skill_info.get('context_importance', 0.5)
            )
    
    def save_job_skills(self, extracted_skills):
        """Backward compatibility method for basic skill extraction"""
        # Clear existing skills for this job to avoid duplicates
        JobSkill.objects.filter(job=self).delete()
        
        for skill_info in extracted_skills:
            # Get or create the skill in the database
            skill, created = Skill.objects.get_or_create(
                name=skill_info['name'],
                defaults={
                    'category': skill_info['category'],
                    'subcategory': skill_info['subcategory']
                }
            )
            
            # Create relationship between job and skill
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
        ordering = ['category', 'subcategory', 'name']
        indexes = [
            models.Index(fields=['category', 'subcategory']),
        ]

class ResumeSkill(models.Model):
    SKILL_LEVELS = [
        ('unspecified', 'Unspecified'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='resumes')
    confidence = models.FloatField(default=1.0)  # Enhanced confidence score from AI analysis
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='unspecified')
    matched_text = models.CharField(max_length=200, blank=True)  # What text was matched
    context = models.TextField(blank=True)  # Context where skill was found
    base_confidence = models.FloatField(default=1.0)  # Base matching confidence
    context_importance = models.FloatField(default=0.5)  # Context importance score
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['resume', 'skill'], name='unique_resume_skill')
        ]

class JobSkill(models.Model):
    SKILL_LEVELS = [
        ('unspecified', 'Unspecified'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='jobs')
    importance = models.FloatField(default=1.0)  # Enhanced importance score from AI analysis
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='unspecified')
    matched_text = models.CharField(max_length=200, blank=True)  # What text was matched
    context = models.TextField(blank=True)  # Context where skill was found
    mention_count = models.IntegerField(default=1)  # How many times mentioned
    position_score = models.FloatField(default=0.5)  # Position importance score
    confidence = models.FloatField(default=1.0)  # Base confidence of detection
    context_importance = models.FloatField(default=0.5)  # Context importance score
    
    class Meta:
        unique_together = ('job', 'skill')