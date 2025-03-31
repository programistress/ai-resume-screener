from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Welcome to Resume Screener API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/resumes/', include('resumes.urls')), 
    path('api/jobs/', include('job_desc.urls')),   
    path('api-auth/', include('rest_framework.urls')),  # add REST framework browsable API
    path('', home),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # helper to serve media files during development.