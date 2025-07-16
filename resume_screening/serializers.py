from rest_framework import serializers
from .models import Resume, JobDescription, ResumeSkill, JobSkill

class EnhancedResumeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    skill_subcategory = serializers.CharField(source='skill.subcategory', read_only=True)
    
    class Meta:
        model = ResumeSkill
        fields = [
            'skill_name', 'skill_category', 'skill_subcategory',
            'confidence', 'skill_level', 'matched_text', 'context',
            'base_confidence', 'context_importance'
        ]

class EnhancedJobSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    skill_subcategory = serializers.CharField(source='skill.subcategory', read_only=True)
    
    class Meta:
        model = JobSkill
        fields = [
            'skill_name', 'skill_category', 'skill_subcategory',
            'importance', 'skill_level', 'matched_text', 'context',
            'mention_count', 'position_score', 'confidence', 'context_importance'
        ]

class ResumeSerializer(serializers.ModelSerializer):
    enhanced_skills = EnhancedResumeSkillSerializer(source='skills', many=True, read_only=True)
    skills_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = ['id', 'file', 'extracted_text', 'uploaded_at', 'enhanced_skills', 'skills_summary']
    
    def get_skills_summary(self, obj):
        skills = obj.skills.all()
        if not skills:
            return {}
        
        return {
            'total_skills': skills.count(),
            'skill_levels': {
                'expert': skills.filter(skill_level='expert').count(),
                'intermediate': skills.filter(skill_level='intermediate').count(),
                'beginner': skills.filter(skill_level='beginner').count(),
                'unspecified': skills.filter(skill_level='unspecified').count(),
            },
            'average_confidence': sum(skill.confidence for skill in skills) / skills.count(),
            'top_skills': [
                {
                    'name': skill.skill.name,
                    'confidence': skill.confidence,
                    'level': skill.skill_level
                }
                for skill in skills.order_by('-confidence')[:5]
            ]
        }

class JobDescriptionSerializer(serializers.ModelSerializer):
    enhanced_skills = EnhancedJobSkillSerializer(source='skills', many=True, read_only=True)
    skills_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = JobDescription
        fields = ['id', 'raw_text', 'uploaded_at', 'resume', 'enhanced_skills', 'skills_summary']
    
    def get_skills_summary(self, obj):
        skills = obj.skills.all()
        if not skills:
            return {}
        
        return {
            'total_skills': skills.count(),
            'skill_levels': {
                'expert': skills.filter(skill_level='expert').count(),
                'intermediate': skills.filter(skill_level='intermediate').count(),
                'beginner': skills.filter(skill_level='beginner').count(),
                'unspecified': skills.filter(skill_level='unspecified').count(),
            },
            'average_importance': sum(skill.importance for skill in skills) / skills.count(),
            'critical_skills': skills.filter(importance__gte=0.8).count(),
            'top_skills': [
                {
                    'name': skill.skill.name,
                    'importance': skill.importance,
                    'level': skill.skill_level
                }
                for skill in skills.order_by('-importance')[:5]
            ]
        }