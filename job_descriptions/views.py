from django.shortcuts import render
from .forms import JobDescUploadForm
from rest_framework import serializers, viewsets
from .models import JobDescription

def upload_job_desc(request):
    if request.method == 'POST':
        form = JobDescUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = JobDescUploadForm()
    return render(request, 'upload.html', {'form': form})

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['raw_text', 'uploaded_at']


class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
