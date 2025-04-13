from rest_framework import serializers, viewsets, status
from .models import JobDescription
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class JobDescriptionUploadAPI(APIView):
    permission_classes = [AllowAny]  # allow anyone to upload without authentication
    
    def post(self, request, *args, **kwargs):
        raw_text = request.data.get('raw_text', '')
        
        if not raw_text.strip():
            return Response({'error': 'Job description text is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        job_desc = JobDescription.objects.create(raw_text=raw_text)
        
        return Response({
            'id': job_desc.id, 
            'message': 'Job description uploaded successfully',
            'raw_text': job_desc.raw_text[:100] + '...' if len(job_desc.raw_text) > 100 else job_desc.raw_text
        }, status=status.HTTP_201_CREATED)

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'raw_text', 'uploaded_at']


class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [AllowAny]
