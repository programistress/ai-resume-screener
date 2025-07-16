#!/usr/bin/env python3
"""
Test script to analyze job descriptions using enhanced job requirements analysis
Run this to see what skills and requirements are detected from a job posting
"""

import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_screener.settings')
django.setup()

from resume_screening.utils.analyze_job_requirements import JobRequirementsAnalyzer

def test_job_analysis():
    """Test job description analysis with enhanced requirements analyzer"""
    
    # Sample job description (you can replace this with actual job posting)
    sample_job = """
    Senior Full Stack Developer - AI/ML Focus
    
    REQUIRED QUALIFICATIONS:
    • 5+ years of professional software development experience
    • Strong proficiency in Python programming and Django framework
    • Expert knowledge of React and modern JavaScript/TypeScript
    • Experience with machine learning libraries (TensorFlow, PyTorch)
    • Solid understanding of PostgreSQL and database optimization
    • Must have experience with AWS cloud services
    • Proficient in Git version control and CI/CD pipelines
    
    PREFERRED QUALIFICATIONS:
    • Advanced degree in Computer Science or related field
    • Experience with Natural Language Processing (NLP) and BERT models
    • Knowledge of Docker and Kubernetes containerization
    • Familiarity with data analysis using Pandas and NumPy
    • Understanding of Agile/Scrum development methodologies
    • Experience with RESTful API development
    
    NICE TO HAVE:
    • Background in AI research or publications
    • Experience with microservices architecture
    • Knowledge of Redis caching solutions
    • Familiarity with monitoring tools like Prometheus or Grafana
    • Understanding of security best practices and OWASP guidelines
    
    We are looking for a passionate developer who can work independently and collaborate effectively with cross-functional teams.
    """
    
    print("🎯 JOB DESCRIPTION ANALYSIS USING ENHANCED ANALYZER")
    print("=" * 65)
    print(f"Job Description:\n{sample_job[:300]}...\n")
    
    # Initialize the analyzer
    analyzer = JobRequirementsAnalyzer()
    
    # Analyze the job description
    print("⚡ Analyzing job requirements...")
    analysis_result = analyzer.analyze(sample_job)
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print("-" * 40)
    summary = analysis_result['skill_summary']
    print(f"Total skills found: {summary['total_skills_found']}")
    print(f"Technical skills: {summary['technical_count']}")
    print(f"Soft skills: {summary['soft_count']}")
    
    # Show all skills sorted by importance
    all_skills = analysis_result['all_skills']
    
    print(f"\n🔧 ALL SKILLS BY IMPORTANCE:")
    print("-" * 70)
    print(f"{'Rank':<4} {'Skill Name':<25} {'Importance':<12} {'Level':<12} {'Context'}")
    print("-" * 70)
    
    for i, skill in enumerate(all_skills, 1):
        importance_bar = "█" * int(skill['importance'] * 10)
        context_importance = "High" if skill['context_importance'] >= 0.8 else "Med" if skill['context_importance'] >= 0.5 else "Low"
        
        print(f"{i:<4} {skill['name']:<25} {skill['importance']:.2f} {importance_bar:<10} {skill['skill_level']:<12} {context_importance}")
        
        # Show detailed info for top 10 skills
        if i <= 10:
            print(f"     📝 Matched: '{skill['matched_text']}' | Mentions: {skill['mention_count']} | Confidence: {skill['confidence']:.2f}")
            print(f"     📍 Context: {skill['context'][:80]}...")
            print()
    
    # Show technical vs soft skills breakdown
    technical_skills = analysis_result['technical_skills']
    soft_skills = analysis_result['soft_skills']
    
    print(f"\n🔧 TOP TECHNICAL SKILLS:")
    print("-" * 40)
    for i, skill in enumerate(technical_skills[:15], 1):
        importance_percentage = skill['importance'] * 100
        print(f"{i:2d}. {skill['name']:<25} {importance_percentage:5.1f}% ({skill['subcategory']})")
    
    if soft_skills:
        print(f"\n💭 SOFT SKILLS:")
        print("-" * 25)
        for i, skill in enumerate(soft_skills, 1):
            importance_percentage = skill['importance'] * 100
            print(f"{i:2d}. {skill['name']:<25} {importance_percentage:5.1f}%")
    
    # Show key phrases (non-skill requirements)
    key_phrases = analysis_result['key_phrases']
    if key_phrases:
        print(f"\n📋 KEY REQUIREMENTS (NON-SKILLS):")
        print("-" * 35)
        for phrase in key_phrases:
            print(f"• {phrase}")
    
    # Show skills by category
    print(f"\n📂 SKILLS BY TECHNICAL CATEGORY:")
    print("-" * 40)
    by_subcategory = {}
    for skill in technical_skills:
        subcat = skill.get('subcategory', 'other')
        if subcat not in by_subcategory:
            by_subcategory[subcat] = []
        by_subcategory[subcat].append(f"{skill['name']} ({skill['importance']:.2f})")
    
    for category, skills in by_subcategory.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for skill in skills[:5]:  # Show top 5 in each category
            print(f"  • {skill}")
    
    # Show importance distribution
    print(f"\n📈 IMPORTANCE DISTRIBUTION:")
    print("-" * 30)
    critical_skills = [s for s in all_skills if s['importance'] >= 0.8]
    important_skills = [s for s in all_skills if 0.6 <= s['importance'] < 0.8]
    nice_to_have = [s for s in all_skills if s['importance'] < 0.6]
    
    print(f"Critical (≥80%):     {len(critical_skills):2d} skills")
    print(f"Important (60-80%):  {len(important_skills):2d} skills") 
    print(f"Nice-to-have (<60%): {len(nice_to_have):2d} skills")
    
    return analysis_result

def test_multiple_jobs():
    """Test with multiple different job descriptions"""
    
    jobs = {
        "Frontend Developer": """
        We're looking for a Frontend Developer with strong React skills.
        Requirements: Expert JavaScript, proficient TypeScript, experience with HTML/CSS.
        Nice to have: Vue.js, Angular, webpack knowledge.
        """,
        
        "Data Scientist": """
        Senior Data Scientist position. Must have Python, machine learning, and statistical analysis experience.
        Required: TensorFlow or PyTorch, SQL databases, data visualization.
        Preferred: NLP experience, AWS/GCP, PhD in relevant field.
        """,
        
        "DevOps Engineer": """
        DevOps Engineer needed. Critical: Docker, Kubernetes, AWS/Azure experience required.
        Must have: CI/CD pipelines, Infrastructure as Code, monitoring tools.
        Plus: Terraform, Ansible, security knowledge.
        """
    }
    
    analyzer = JobRequirementsAnalyzer()
    
    print("\n" + "="*80)
    print("🔄 TESTING MULTIPLE JOB TYPES")
    print("="*80)
    
    for job_title, job_desc in jobs.items():
        print(f"\n📋 {job_title.upper()}:")
        print("-" * 50)
        
        result = analyzer.analyze(job_desc)
        top_skills = result['skill_summary']['top_skills']
        
        print("Top 5 most important skills:")
        for i, skill in enumerate(top_skills[:5], 1):
            print(f"  {i}. {skill['name']} ({skill['importance']:.2f})")

if __name__ == "__main__":
    # Test with sample job description
    test_job_analysis()
    
    # Test with multiple job types
    test_multiple_jobs()
    
    print(f"\n💡 TIP: You can modify the sample_job variable in this script")
    print(f"to test with your own job descriptions!") 