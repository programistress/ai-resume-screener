from rest_framework import serializers
from .models import Resume, JobDescription

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'file', 'extracted_text', 'uploaded_at']

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'raw_text', 'uploaded_at', 'resume']