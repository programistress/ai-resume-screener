from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Welcome to Resume Screener API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('resume_screening.urls')),
    path('api-auth/', include('rest_framework.urls')),  # REST framework browsable API
    path('', home),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # serve media files during development