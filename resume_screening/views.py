from .models import Resume, JobDescription
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from .serializers import JobDescriptionSerializer, ResumeSerializer
from .utils.analyze_job_requirements import analyze_job_requirements
from resume_screening.utils.skill_matching import calculate_skill_match

#i removed the forms and now validation is here
#receives file, checks if it exists, creates resume object, saves the resume

class ResumeUploadAPI(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        resume = Resume(file=file)
        try:
            resume.full_clean()  
            resume.save()
            return Response({
                'id': resume.id,
                'message': 'Resume uploaded successfully',
                'extracted_text': resume.extracted_text
            }, status=201)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

#viewsets provide API for interacting with resume and jobdesc models

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [AllowAny]

    # adding a custom endpoint to get job descriptions for a specific resume
    @action(detail=True, methods=['get'])
    def job_descriptions(self, request, pk=None):
        resume = self.get_object()
        jobs = resume.job_descriptions.all() #using the related name
        serializer = JobDescriptionSerializer(jobs, many=True)
        return Response(serializer.data)
        
class JobDescriptionUploadAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        raw_text = request.data.get('raw_text', '')
        resume_id = request.data.get('resume_id')
        
        if not raw_text.strip():
            return Response({'error': 'Job description text is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        job_desc = JobDescription(raw_text=raw_text)

        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id)
                job_desc.resume = resume
            except Resume.DoesNotExist:
                return Response({'error': 'Resume not found'}, 
                               status=status.HTTP_404_NOT_FOUND)
        
        job_desc.save()
        
        return Response({
            'id': job_desc.id, 
            'message': 'Job description uploaded successfully',
            'raw_text': job_desc.raw_text[:100] + '...' if len(job_desc.raw_text) > 100 else job_desc.raw_text,
            'resume_id': job_desc.resume.id if job_desc.resume else None
        }, status=status.HTTP_201_CREATED)
    
class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [AllowAny]
    
    # override get_queryset to allow filtering by resume_id
    def get_queryset(self):
        queryset = JobDescription.objects.all()
        resume_id = self.request.query_params.get('resume_id')
        if resume_id is not None:
            queryset = queryset.filter(resume_id=resume_id)
        return queryset
    
class JobAnalysisAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, job_id, *args, **kwargs):
        try:
            job = JobDescription.objects.get(id=job_id)

            requirements = analyze_job_requirements(job.raw_text)
            
            return Response({
                'job_id': job.id,
                'requirements': requirements
            }, status=status.HTTP_200_OK)
            
        except JobDescription.DoesNotExist:
            return Response({'error': 'Job description not found'}, status=status.HTTP_404_NOT_FOUND)
        
class SkillMatchingAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, resume_id, job_id, *args, **kwargs):
        try:
            # verify the resume and job description exist
            resume = Resume.objects.get(id=resume_id)
            job = JobDescription.objects.get(id=job_id)
            
            match_results = calculate_skill_match(resume_id, job_id)
            
            return Response({
                'resume_id': resume_id,
                'job_id': job_id,
                'match_results': match_results
            }, status=status.HTTP_200_OK)
            
        except (Resume.DoesNotExist, JobDescription.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)