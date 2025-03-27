from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    return HttpResponse("Welcome to Resume Screener!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('resume/', include('resumes.urls')),
    path('jobdesc/', include('job_descriptions.urls')),
    path('', home), 
]
