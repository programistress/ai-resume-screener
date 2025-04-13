from django.urls import path, include
from .views import JobDescriptionUploadAPI, JobDescriptionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'descriptions', JobDescriptionViewSet)


urlpatterns = [
     # API endpoint for uploading job descriptions
    path('upload/', JobDescriptionUploadAPI.as_view(), name='job_desc_upload_api'),
    
    # include the router URLs for listing and retrieving job descriptions
    path('', include(router.urls)),
]