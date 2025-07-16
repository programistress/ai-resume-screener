#!/usr/bin/env python3
"""
Demo script for enhanced AI resume screening system
This will upload test data and demonstrate the enhanced analysis capabilities
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def demo_enhanced_system():
    """Demonstrate the enhanced system with real API calls"""
    
    print("🎯 ENHANCED AI RESUME SCREENER DEMO")
    print("=" * 50)
    
    # Sample job description for upload
    job_data = {
        "raw_text": """
        Senior Python Developer - AI/ML Team
        
        REQUIRED QUALIFICATIONS:
        • Must have 5+ years Python programming experience
        • Expert knowledge of Django framework required
        • Strong React and JavaScript/TypeScript skills essential
        • PostgreSQL database experience mandatory
        • AWS cloud platform experience required
        • Machine learning model deployment experience needed
        
        PREFERRED QUALIFICATIONS:
        • Advanced TensorFlow or PyTorch experience highly desired
        • Docker and Kubernetes containerization skills
        • Natural Language Processing (NLP) background a plus
        • CI/CD pipeline setup experience
        • Data analysis with pandas/NumPy
        • Redis caching experience beneficial
        
        NICE TO HAVE:
        • GraphQL API development
        • Monitoring tools (Prometheus, Grafana)
        • Microservices architecture experience
        """
    }
    
    try:
        print("📤 Step 1: Uploading Job Description...")
        job_response = requests.post(f"{BASE_URL}/jobs/upload/", json=job_data)
        
        if job_response.status_code == 201:
            job_data_resp = job_response.json()
            job_id = job_data_resp['id']
            print(f"   ✅ Job uploaded successfully! ID: {job_id}")
            print(f"   Preview: {job_data_resp.get('raw_text', '')}")
        else:
            print(f"   ❌ Failed to upload job: {job_response.text}")
            return
        
        # Wait a moment for processing
        print("\n⏳ Processing job requirements with AI...")
        time.sleep(2)
        
        print("\n🔍 Step 2: Getting Enhanced Job Analysis...")
        analysis_response = requests.get(f"{BASE_URL}/jobs/{job_id}/analysis/")
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            print("   ✅ Enhanced analysis complete!")
            
            summary = analysis_data.get('summary', {})
            print(f"   📊 Analysis Summary:")
            print(f"      Total skills detected: {summary.get('total_skills', 0)}")
            print(f"      Technical skills: {summary.get('technical_skills', 0)}")
            print(f"      Soft skills: {summary.get('soft_skills', 0)}")
            
            top_skills = summary.get('top_skills', [])
            if top_skills:
                print(f"   🏆 Top Required Skills:")
                for i, skill in enumerate(top_skills[:5], 1):
                    importance = skill.get('importance', 0) * 100
                    level = skill.get('skill_level', 'unspecified')
                    print(f"      {i}. {skill.get('name', 'Unknown')} - {importance:.1f}% importance ({level})")
        else:
            print(f"   ❌ Failed to get analysis: {analysis_response.text}")
            
        print("\n🔍 Step 3: Testing with Existing Resume...")
        
        # Try to get resumes list to see if any exist
        resumes_response = requests.get(f"{BASE_URL}/resumes/")
        
        if resumes_response.status_code == 200:
            resumes_data = resumes_response.json()
            
            if isinstance(resumes_data, list) and len(resumes_data) > 0:
                resume = resumes_data[0]
                resume_id = resume['id']
                print(f"   ✅ Found existing resume ID: {resume_id}")
                
                # Test enhanced resume analysis
                print("\n🧠 Step 4: Enhanced Resume Analysis...")
                resume_analysis_response = requests.get(f"{BASE_URL}/resumes/{resume_id}/enhanced-analysis/")
                
                if resume_analysis_response.status_code == 200:
                    resume_analysis = resume_analysis_response.json()
                    print("   ✅ Enhanced resume analysis complete!")
                    
                    resume_summary = resume_analysis.get('summary', {})
                    print(f"   📊 Resume Summary:")
                    print(f"      Total skills detected: {resume_summary.get('total_skills', 0)}")
                    print(f"      Technical skills: {resume_summary.get('technical_count', 0)}")
                    print(f"      Soft skills: {resume_summary.get('soft_count', 0)}")
                    
                    skill_levels = resume_summary.get('skill_levels', {})
                    print(f"   📈 Skill Levels:")
                    print(f"      Expert: {skill_levels.get('expert', 0)}")
                    print(f"      Intermediate: {skill_levels.get('intermediate', 0)}")
                    print(f"      Beginner: {skill_levels.get('beginner', 0)}")
                    
                    top_skills = resume_summary.get('top_skills', [])
                    if top_skills:
                        print(f"   🏆 Top Skills:")
                        for i, skill in enumerate(top_skills[:5], 1):
                            confidence = skill.get('confidence', 0) * 100
                            level = skill.get('level', 'unspecified')
                            print(f"      {i}. {skill.get('name', 'Unknown')} - {confidence:.1f}% confidence ({level})")
                
                # Test enhanced matching
                print("\n🤝 Step 5: Enhanced Skill Matching...")
                matching_response = requests.get(f"{BASE_URL}/skills/enhanced-match/{resume_id}/{job_id}/")
                
                if matching_response.status_code == 200:
                    matching_data = matching_response.json()
                    print("   ✅ Enhanced matching analysis complete!")
                    
                    matching_analysis = matching_data.get('matching_analysis', {})
                    recommendations = matching_data.get('recommendations', {})
                    
                    overall_score = matching_analysis.get('overall_score', 0) * 100
                    print(f"   🏆 Overall Compatibility: {overall_score:.1f}%")
                    print(f"   📊 Rating: {recommendations.get('recommendation', 'Unknown')}")
                    print(f"   💬 Message: {recommendations.get('message', 'No message')}")
                    
                    stats = matching_analysis.get('stats', {})
                    print(f"   📈 Match Statistics:")
                    print(f"      Skills matched: {stats.get('matched_skills', 0)}/{stats.get('total_job_skills', 0)}")
                    print(f"      Missing skills: {stats.get('missing_skills', 0)}")
                    print(f"      Extra skills: {stats.get('extra_skills', 0)}")
                    
                    # Show top matches
                    matches = matching_analysis.get('matches', [])
                    if matches:
                        print(f"   ✅ Top Skill Matches:")
                        for i, match in enumerate(matches[:3], 1):
                            quality = match.get('match_quality', 0) * 100
                            print(f"      {i}. {match.get('skill_name', 'Unknown')} - {quality:.1f}% match quality")
                    
                    # Show critical gaps
                    missing = matching_analysis.get('missing_skills', [])
                    critical_missing = [s for s in missing if s.get('importance', 0) >= 0.7]
                    if critical_missing:
                        print(f"   ❌ Critical Missing Skills:")
                        for skill in critical_missing[:3]:
                            importance = skill.get('importance', 0) * 100
                            print(f"      • {skill.get('skill_name', 'Unknown')} - {importance:.1f}% importance")
                else:
                    print(f"   ❌ Failed to get matching analysis: {matching_response.text}")
                    
            else:
                print("   📝 No existing resumes found. Upload a resume first!")
                print("   💡 Use: curl -X POST http://localhost:8000/api/resumes/upload/ -F 'file=@your_resume.pdf'")
        else:
            print(f"   ❌ Failed to get resumes: {resumes_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server!")
        print("💡 Make sure Django server is running: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return
    
    print(f"\n🎉 ENHANCED SYSTEM DEMO COMPLETE!")
    print("=" * 45)
    print("The enhanced AI system provides:")
    print("✅ Semantic understanding with BERT")
    print("✅ Confidence scoring for accuracy")
    print("✅ Context-aware skill importance")
    print("✅ Intelligent matching recommendations")
    print("✅ Professional hiring insights")

if __name__ == "__main__":
    demo_enhanced_system() 