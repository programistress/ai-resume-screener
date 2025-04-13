from .forms import ResumeUploadForm
from rest_framework import serializers, viewsets, status
from .models import Resume
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class ResumeUploadAPI(APIView):
    parser_classes = (MultiPartParser)
    permission_classes = [AllowAny]  # allow anyone to upload without authentication
    
    def post(self, request, *args, **kwargs):
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            return Response({
                'id': resume.id, 
                'message': 'Resume uploaded successfully',
                'extracted_text': resume.extracted_text,
            }, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
#serializer for the Resume model
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['file', 'extracted_text', 'uploaded_at']

#viewset to interact with Resume data
class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer