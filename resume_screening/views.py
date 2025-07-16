from .models import Resume, JobDescription
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from .serializers import JobDescriptionSerializer, ResumeSerializer
from .utils.analyze_job_requirements import JobRequirementsAnalyzer
from resume_screening.utils.skill_matching import calculate_skill_match
from .utils.enhanced_skill_extraction import EnhancedSkillExtractor

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

            # Use enhanced job requirements analyzer
            analyzer = JobRequirementsAnalyzer()
            requirements = analyzer.analyze(job.raw_text)
            
            return Response({
                'job_id': job.id,
                'analysis': requirements,
                'summary': {
                    'total_skills': requirements['skill_summary']['total_skills_found'],
                    'technical_skills': requirements['skill_summary']['technical_count'],
                    'soft_skills': requirements['skill_summary']['soft_count'],
                    'top_skills': requirements['skill_summary']['top_skills'][:10]
                }
            }, status=status.HTTP_200_OK)
            
        except JobDescription.DoesNotExist:
            return Response({'error': 'Job description not found'}, status=status.HTTP_404_NOT_FOUND)

class EnhancedResumeAnalysisAPI(APIView):
    """New API endpoint for enhanced resume skill analysis"""
    permission_classes = [AllowAny]
    
    def get(self, request, resume_id, *args, **kwargs):
        try:
            resume = Resume.objects.get(id=resume_id)
            
            if not resume.extracted_text:
                return Response({'error': 'No text extracted from resume'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Use enhanced skill extractor
            extractor = EnhancedSkillExtractor()
            extracted_skills = extractor.extract_skills_with_confidence(resume.extracted_text)
            
            # Sort skills by confidence
            extracted_skills.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Separate technical and soft skills
            technical_skills = [s for s in extracted_skills if s['category'] == 'technical']
            soft_skills = [s for s in extracted_skills if s['category'] == 'soft']
            
            return Response({
                'resume_id': resume.id,
                'analysis': {
                    'all_skills': extracted_skills,
                    'technical_skills': technical_skills,
                    'soft_skills': soft_skills
                },
                'summary': {
                    'total_skills': len(extracted_skills),
                    'technical_count': len(technical_skills),
                    'soft_count': len(soft_skills),
                    'top_skills': extracted_skills[:10],
                    'skill_levels': {
                        'expert': len([s for s in extracted_skills if s.get('skill_level') == 'expert']),
                        'intermediate': len([s for s in extracted_skills if s.get('skill_level') == 'intermediate']),
                        'beginner': len([s for s in extracted_skills if s.get('skill_level') == 'beginner'])
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Resume.DoesNotExist:
            return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
        
class EnhancedSkillMatchingAPI(APIView):
    """Enhanced skill matching using AI-powered analysis"""
    permission_classes = [AllowAny]
    
    def get(self, request, resume_id, job_id, *args, **kwargs):
        try:
            # Verify the resume and job description exist
            resume = Resume.objects.get(id=resume_id)
            job = JobDescription.objects.get(id=job_id)
            
            if not resume.extracted_text:
                return Response({'error': 'No text extracted from resume'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Use enhanced analyzers
            skill_extractor = EnhancedSkillExtractor()
            job_analyzer = JobRequirementsAnalyzer()
            
            # Analyze resume and job
            resume_skills = skill_extractor.extract_skills_with_confidence(resume.extracted_text)
            job_analysis = job_analyzer.analyze(job.raw_text)
            
            # Calculate enhanced matching score
            matching_result = self.calculate_enhanced_matching_score(resume_skills, job_analysis)
            
            return Response({
                'resume_id': resume_id,
                'job_id': job_id,
                'matching_analysis': matching_result,
                'recommendations': self.generate_recommendations(matching_result)
            }, status=status.HTTP_200_OK)
            
        except (Resume.DoesNotExist, JobDescription.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def calculate_enhanced_matching_score(self, resume_skills, job_requirements):
        """Calculate compatibility score between resume and job using enhanced analysis"""
        
        job_skills = job_requirements['all_skills']
        
        # Create skill name mappings for easy lookup
        resume_skill_map = {skill['name'].lower(): skill for skill in resume_skills}
        job_skill_map = {skill['name'].lower(): skill for skill in job_skills}
        
        matches = []
        missing_skills = []
        extra_skills = []
        
        # Calculate total job importance
        total_job_importance = sum(skill['importance'] for skill in job_skills)
        matched_importance = 0
        
        # Find matches and missing skills
        for job_skill in job_skills:
            job_skill_name = job_skill['name'].lower()
            if job_skill_name in resume_skill_map:
                resume_skill = resume_skill_map[job_skill_name]
                match_info = {
                    'skill_name': job_skill['name'],
                    'job_importance': job_skill['importance'],
                    'resume_confidence': resume_skill['confidence'],
                    'job_level': job_skill.get('skill_level', 'unspecified'),
                    'resume_level': resume_skill.get('skill_level', 'unspecified'),
                    'match_quality': (job_skill['importance'] + resume_skill['confidence']) / 2
                }
                matches.append(match_info)
                matched_importance += job_skill['importance']
            else:
                missing_skills.append({
                    'skill_name': job_skill['name'],
                    'importance': job_skill['importance'],
                    'level': job_skill.get('skill_level', 'unspecified')
                })
        
        # Find extra skills in resume
        for resume_skill in resume_skills:
            resume_skill_name = resume_skill['name'].lower()
            if resume_skill_name not in job_skill_map:
                extra_skills.append({
                    'skill_name': resume_skill['name'],
                    'confidence': resume_skill['confidence'],
                    'level': resume_skill.get('skill_level', 'unspecified')
                })
        
        # Calculate scores
        importance_score = matched_importance / total_job_importance if total_job_importance > 0 else 0
        skill_coverage = len(matches) / len(job_skills) if job_skills else 0
        
        # Weighted final score
        overall_score = (importance_score * 0.7) + (skill_coverage * 0.3)
        
        return {
            'overall_score': overall_score,
            'importance_score': importance_score,
            'skill_coverage': skill_coverage,
            'matches': sorted(matches, key=lambda x: x['match_quality'], reverse=True),
            'missing_skills': sorted(missing_skills, key=lambda x: x['importance'], reverse=True),
            'extra_skills': sorted(extra_skills, key=lambda x: x['confidence'], reverse=True),
            'stats': {
                'total_job_skills': len(job_skills),
                'matched_skills': len(matches),
                'missing_skills': len(missing_skills),
                'extra_skills': len(extra_skills)
            }
        }
    
    def generate_recommendations(self, matching_result):
        """Generate hiring recommendations based on matching analysis"""
        
        overall_score = matching_result['overall_score'] * 100
        critical_missing = [s for s in matching_result['missing_skills'] if s['importance'] >= 0.7]
        
        if overall_score >= 80:
            recommendation = "EXCELLENT_MATCH"
            message = "Strong candidate! Highly recommended for interview."
            priority = "HIGH"
        elif overall_score >= 60:
            recommendation = "GOOD_MATCH"
            message = "Good candidate with minor gaps. Recommended for interview."
            priority = "MEDIUM"
        elif overall_score >= 40:
            recommendation = "PARTIAL_MATCH"
            message = "Potential candidate with some gaps. Consider for interview if training is available."
            priority = "LOW"
        else:
            recommendation = "POOR_MATCH"
            message = "Significant skill gaps. May not be suitable for this role."
            priority = "VERY_LOW"
        
        return {
            'recommendation': recommendation,
            'message': message,
            'priority': priority,
            'score_percentage': round(overall_score, 1),
            'critical_gaps': len(critical_missing),
            'suggestions': [
                "Review critical missing skills during interview" if critical_missing else "No critical gaps identified",
                f"Consider training opportunities for {len(matching_result['missing_skills'])} missing skills" if matching_result['missing_skills'] else "No additional training needed"
            ]
        }

# Keep the old API for backward compatibility
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