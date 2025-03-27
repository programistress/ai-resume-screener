from django.urls import path
from .views import upload_job_desc

urlpatterns = [
    path('upload/', upload_job_desc, name='upload_job_desc'),
]