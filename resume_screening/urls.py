from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResumeUploadAPI, 
    ResumeViewSet,
    JobDescriptionUploadAPI,
    JobDescriptionViewSet,
    JobAnalysisAPI,
    SkillMatchingAPI,
    EnhancedResumeAnalysisAPI,
    EnhancedSkillMatchingAPI
)

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet)
router.register(r'job-descriptions', JobDescriptionViewSet)

urlpatterns = [
    # resume endpoints
    path('resumes/upload/', ResumeUploadAPI.as_view(), name='resume_upload_api'),
    
    # jobdesc endpoints
    path('jobs/upload/', JobDescriptionUploadAPI.as_view(), name='job_desc_upload_api'),
    
    # router URLs
    path('', include(router.urls)),

    # Analysis endpoints
    path('jobs/<int:job_id>/analysis/', JobAnalysisAPI.as_view(), name='job_analysis_api'),
    path('resumes/<int:resume_id>/enhanced-analysis/', EnhancedResumeAnalysisAPI.as_view(), name='enhanced_resume_analysis_api'),
    
    # Skill matching endpoints  
    path('skills/match/<int:resume_id>/<int:job_id>/', SkillMatchingAPI.as_view(), name='skill_matching_api'),
    path('skills/enhanced-match/<int:resume_id>/<int:job_id>/', EnhancedSkillMatchingAPI.as_view(), name='enhanced_skill_matching_api')
]