from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeUploadAPI, ResumeViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet)

urlpatterns = [
    # API endpoint for uploading resumes
    path('upload/', ResumeUploadAPI.as_view(), name='resume_upload_api'),
    
    # the router URLs for listing and retrieving resumes
    path('', include(router.urls)),
]