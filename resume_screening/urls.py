from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResumeUploadAPI, 
    ResumeViewSet,
    JobDescriptionUploadAPI,
    JobDescriptionViewSet
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
]