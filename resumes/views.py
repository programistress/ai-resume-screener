from django.shortcuts import render
from .forms import ResumeUploadForm
from rest_framework import serializers, viewsets
from .models import Resume

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = ResumeUploadForm()
    return render(request, 'upload.html', {'form': form})

#serializer for the Resume model
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['file', 'extracted_text', 'uploaded_at']

#viewset to interact with Resume data
class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer