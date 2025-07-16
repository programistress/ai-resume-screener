#!/usr/bin/env python3
"""
Test script for complete resume-job matching analysis
Shows how well a resume matches a job description using enhanced AI analysis
"""

import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_screener.settings')
django.setup()

from resume_screening.utils.enhanced_skill_extraction import EnhancedSkillExtractor
from resume_screening.utils.analyze_job_requirements import JobRequirementsAnalyzer
from resume_screening.utils.text_extraction import extract_text

def calculate_matching_score(resume_skills, job_requirements):
    """Calculate compatibility score between resume and job"""
    
    job_skills = job_requirements['all_skills']
    
    # Create skill name to info mapping for easy lookup
    resume_skill_map = {skill['name'].lower(): skill for skill in resume_skills}
    job_skill_map = {skill['name'].lower(): skill for skill in job_skills}
    
    matches = []
    missing_skills = []
    extra_skills = []
    
    # Find matches and missing skills
    total_job_importance = sum(skill['importance'] for skill in job_skills)
    matched_importance = 0
    
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
    
    # Calculate overall score
    if total_job_importance > 0:
        importance_score = matched_importance / total_job_importance
    else:
        importance_score = 0
    
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

def test_resume_job_matching():
    """Test complete resume-job matching workflow"""
    
    # Sample resume
    sample_resume = """
    Sarah Chen - Senior Software Engineer
    
    EXPERIENCE:
    • 6+ years developing web applications with Python and Django
    • Expert-level React and TypeScript development (4 years)
    • Strong experience with PostgreSQL database design and optimization
    • Proficient in AWS cloud services (EC2, S3, Lambda, RDS)
    • Advanced Git workflows and CI/CD pipeline implementation
    • Machine learning model development using TensorFlow and Scikit-learn
    • Experience with Docker containerization and deployment
    
    SKILLS:
    • Programming: Python (Expert), JavaScript/TypeScript (Advanced), SQL (Intermediate)
    • Frameworks: Django, React, FastAPI, Flask
    • Cloud: AWS (proficient), basic Azure knowledge
    • Data: pandas, NumPy, data analysis, some NLP experience
    • DevOps: Docker, basic Kubernetes, Jenkins CI/CD
    • Databases: PostgreSQL, MySQL, some MongoDB
    """
    
    # Sample job description
    sample_job = """
    Senior Full Stack Developer - AI Team
    
    REQUIRED SKILLS:
    • Must have 5+ years Python programming experience
    • Expert knowledge of React and modern JavaScript frameworks required
    • Strong Django or FastAPI backend development skills essential
    • PostgreSQL database experience mandatory
    • AWS cloud platform experience required
    • Machine learning model deployment experience needed
    
    PREFERRED QUALIFICATIONS:
    • Advanced TypeScript knowledge preferred
    • TensorFlow or PyTorch experience highly desired
    • Docker and Kubernetes containerization skills
    • Natural Language Processing (NLP) background a plus
    • CI/CD pipeline setup experience
    • Data analysis with pandas/NumPy
    
    NICE TO HAVE:
    • Redis caching experience
    • GraphQL API development
    • Monitoring tools (Prometheus, Grafana)
    """
    
    print("🎯 RESUME-JOB MATCHING ANALYSIS")
    print("=" * 50)
    
    # Initialize analyzers
    skill_extractor = EnhancedSkillExtractor()
    job_analyzer = JobRequirementsAnalyzer()
    
    print("📄 STEP 1: Analyzing Resume...")
    resume_skills = skill_extractor.extract_skills_with_confidence(sample_resume)
    resume_skills.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"   ✅ Found {len(resume_skills)} skills in resume")
    print("   Top resume skills:")
    for skill in resume_skills[:5]:
        print(f"     • {skill['name']} ({skill['confidence']:.2f} confidence, {skill['skill_level']} level)")
    
    print("\n🎯 STEP 2: Analyzing Job Requirements...")
    job_analysis = job_analyzer.analyze(sample_job)
    
    job_summary = job_analysis['skill_summary']
    print(f"   ✅ Found {job_summary['total_skills_found']} skills in job description")
    print("   Top job requirements:")
    for skill in job_analysis['all_skills'][:5]:
        print(f"     • {skill['name']} ({skill['importance']:.2f} importance, {skill.get('skill_level', 'unspecified')} level)")
    
    print("\n🔄 STEP 3: Calculating Match Score...")
    matching_result = calculate_matching_score(resume_skills, job_analysis)
    
    # Display results
    overall_score = matching_result['overall_score'] * 100
    importance_score = matching_result['importance_score'] * 100
    coverage_score = matching_result['skill_coverage'] * 100
    
    print(f"\n📊 MATCHING RESULTS:")
    print("=" * 40)
    print(f"🏆 Overall Compatibility: {overall_score:.1f}%")
    print(f"⭐ Importance Match:      {importance_score:.1f}%")
    print(f"📈 Skill Coverage:        {coverage_score:.1f}%")
    
    # Score interpretation
    if overall_score >= 80:
        rating = "🟢 EXCELLENT MATCH"
    elif overall_score >= 60:
        rating = "🟡 GOOD MATCH" 
    elif overall_score >= 40:
        rating = "🟠 PARTIAL MATCH"
    else:
        rating = "🔴 POOR MATCH"
    
    print(f"\nRating: {rating}")
    
    # Show detailed breakdown
    stats = matching_result['stats']
    print(f"\n📋 DETAILED BREAKDOWN:")
    print("-" * 30)
    print(f"Job requires:     {stats['total_job_skills']} skills")
    print(f"Resume matches:   {stats['matched_skills']} skills")
    print(f"Missing:          {stats['missing_skills']} skills")
    print(f"Extra skills:     {stats['extra_skills']} skills")
    
    # Show matched skills
    matches = matching_result['matches']
    print(f"\n✅ MATCHED SKILLS ({len(matches)}):")
    print("-" * 50)
    for i, match in enumerate(matches[:10], 1):
        quality_bar = "█" * int(match['match_quality'] * 10)
        print(f"{i:2d}. {match['skill_name']:<20} Quality: {match['match_quality']:.2f} {quality_bar}")
        print(f"     Job: {match['job_importance']:.2f} importance ({match['job_level']})")
        print(f"     Resume: {match['resume_confidence']:.2f} confidence ({match['resume_level']})")
        print()
    
    # Show missing critical skills
    missing = matching_result['missing_skills']
    critical_missing = [s for s in missing if s['importance'] >= 0.7]
    
    if critical_missing:
        print(f"\n❌ CRITICAL MISSING SKILLS:")
        print("-" * 30)
        for skill in critical_missing:
            importance_percentage = skill['importance'] * 100
            print(f"• {skill['skill_name']:<20} {importance_percentage:5.1f}% importance ({skill['level']} level)")
    
    # Show all missing skills
    if missing:
        print(f"\n📝 ALL MISSING SKILLS ({len(missing)}):")
        print("-" * 35)
        for i, skill in enumerate(missing, 1):
            importance_percentage = skill['importance'] * 100
            priority = "HIGH" if skill['importance'] >= 0.7 else "MED" if skill['importance'] >= 0.4 else "LOW"
            print(f"{i:2d}. {skill['skill_name']:<25} {importance_percentage:5.1f}% ({priority})")
    
    # Show extra skills
    extra = matching_result['extra_skills']
    if extra:
        print(f"\n➕ ADDITIONAL SKILLS IN RESUME ({len(extra)}):")
        print("-" * 45)
        for i, skill in enumerate(extra[:10], 1):
            confidence_percentage = skill['confidence'] * 100
            print(f"{i:2d}. {skill['skill_name']:<25} {confidence_percentage:5.1f}% confidence")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 25)
    if overall_score >= 70:
        print("✅ Strong candidate! Consider for interview.")
        if critical_missing:
            print("💼 Address these critical gaps during interview.")
    elif overall_score >= 50:
        print("🤔 Potential candidate with some gaps.")
        print("📚 Consider training opportunities for missing skills.")
    else:
        print("❌ Significant skill gaps. May not be suitable.")
        print("🎯 Focus on candidates with higher match scores.")
    
    return matching_result

def test_with_files(resume_file, job_file):
    """Test with actual resume and job files"""
    print(f"📁 TESTING WITH FILES:")
    print(f"Resume: {resume_file}")
    print(f"Job: {job_file}")
    print("-" * 50)
    
    try:
        # Extract text from files
        if resume_file.endswith(('.pdf', '.docx')):
            resume_text = extract_text(resume_file)
            if not resume_text:
                print("❌ No text could be extracted from resume file")
                return
        else:
            resume_text = open(resume_file).read()
            
        job_text = open(job_file).read()
        
        # Analyze
        skill_extractor = EnhancedSkillExtractor()
        job_analyzer = JobRequirementsAnalyzer()
        
        resume_skills = skill_extractor.extract_skills_with_confidence(resume_text)
        job_analysis = job_analyzer.analyze(job_text)
        matching_result = calculate_matching_score(resume_skills, job_analysis)
        
        # Show quick results
        score = matching_result['overall_score'] * 100
        print(f"📊 Compatibility Score: {score:.1f}%")
        print(f"📈 Skills Matched: {matching_result['stats']['matched_skills']}/{matching_result['stats']['total_job_skills']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Test with provided files
        test_with_files(sys.argv[1], sys.argv[2])
    else:
        # Test with sample data
        test_resume_job_matching()
        
        print(f"\n💡 TIP: You can test with actual files:")
        print(f"python test_resume_job_matching.py resume.pdf job_description.txt") 