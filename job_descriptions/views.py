from django.shortcuts import render
from .forms import JobDescUploadForm
from rest_framework import serializers, viewsets, status
from .models import JobDescription
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class JobDescriptionUploadAPI(APIView):
    permission_classes = [AllowAny]  # allow anyone to upload without authentication
    
    def post(self, request, *args, **kwargs):
        form = JobDescUploadForm(request.POST)
        if form.is_valid():
            job_desc = form.save()
            return Response({
                'id': job_desc.id, 
                'message': 'Job description uploaded successfully',
                'raw_text': job_desc.raw_text[:50] + '...' if len(job_desc.raw_text) > 50 else job_desc.raw_text
            }, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['raw_text', 'uploaded_at']


class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
