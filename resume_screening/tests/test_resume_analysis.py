#!/usr/bin/env python3
"""
Test script to analyze a resume using enhanced skill extraction
Run this to see what skills are detected from a resume with confidence scores
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
from resume_screening.utils.text_extraction import extract_text

def test_resume_analysis():
    """Test resume analysis with enhanced skill extraction"""
    
    # Sample resume text (you can replace this with actual resume content)
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    EXPERIENCE:
    Software Engineer at TechCorp (2020-2023)
    - Developed scalable web applications using Python and Django
    - Built responsive frontends with React and TypeScript 
    - Implemented machine learning models using TensorFlow and Scikit-learn
    - Strong experience with AWS cloud services and Docker containerization
    - Proficient in PostgreSQL database design and optimization
    - Advanced knowledge of Git version control and CI/CD pipelines
    
    SKILLS:
    • Expert-level Python programming (5+ years)
    • Strong React and JavaScript development
    • Intermediate knowledge of Machine Learning and NLP
    • Experience with AWS, Docker, Kubernetes
    • Familiar with data analysis using Pandas and NumPy
    • Good understanding of Agile/Scrum methodologies
    
    EDUCATION:
    BS Computer Science, University of Tech (2020)
    """
    
    print("🔍 RESUME ANALYSIS USING ENHANCED SKILL EXTRACTION")
    print("=" * 60)
    print(f"Resume Text:\n{sample_resume[:200]}...\n")
    
    # Initialize the enhanced extractor
    extractor = EnhancedSkillExtractor()
    
    # Extract skills with confidence
    print("⚡ Extracting skills...")
    extracted_skills = extractor.extract_skills_with_confidence(sample_resume)
    
    # Sort by confidence (highest first)
    extracted_skills.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n📊 FOUND {len(extracted_skills)} SKILLS:")
    print("-" * 60)
    
    # Group skills by category
    technical_skills = [s for s in extracted_skills if s['category'] == 'technical']
    soft_skills = [s for s in extracted_skills if s['category'] == 'soft']
    
    print(f"\n🔧 TECHNICAL SKILLS ({len(technical_skills)}):")
    for i, skill in enumerate(technical_skills, 1):
        confidence_bar = "█" * int(skill['confidence'] * 10)
        print(f"{i:2d}. {skill['name']:<25} | Confidence: {skill['confidence']:.2f} {confidence_bar}")
        print(f"     Level: {skill['skill_level']:<12} | Matched: '{skill['matched_text']}'")
        print(f"     Context: {skill['context'][:100]}...")
        print()
    
    if soft_skills:
        print(f"\n💭 SOFT SKILLS ({len(soft_skills)}):")
        for i, skill in enumerate(soft_skills, 1):
            confidence_bar = "█" * int(skill['confidence'] * 10)
            print(f"{i:2d}. {skill['name']:<25} | Confidence: {skill['confidence']:.2f} {confidence_bar}")
            print(f"     Level: {skill['skill_level']:<12} | Matched: '{skill['matched_text']}'")
            print()
    
    # Show top 10 most confident skills
    print(f"\n🏆 TOP 10 MOST CONFIDENT SKILLS:")
    print("-" * 40)
    for i, skill in enumerate(extracted_skills[:10], 1):
        confidence_percentage = skill['confidence'] * 100
        print(f"{i:2d}. {skill['name']:<20} {confidence_percentage:5.1f}%")
    
    # Show skills by subcategory
    print(f"\n📂 SKILLS BY CATEGORY:")
    print("-" * 30)
    by_category = {}
    for skill in extracted_skills:
        category = skill.get('subcategory', 'other')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(skill['name'])
    
    for category, skills in by_category.items():
        print(f"{category.replace('_', ' ').title()}: {', '.join(skills)}")
    
    return extracted_skills

def test_with_file(file_path):
    """Test with an actual resume file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📄 ANALYZING RESUME FILE: {file_path}")
    print("=" * 60)
    
    # Extract text from file
    try:
        resume_text = extract_text(file_path)
        if not resume_text:
            print("❌ No text could be extracted from the file")
            return
            
        print(f"✅ Extracted {len(resume_text)} characters from file")
        print(f"First 300 characters:\n{resume_text[:300]}...\n")
        
        # Analyze with enhanced extractor
        extractor = EnhancedSkillExtractor()
        extracted_skills = extractor.extract_skills_with_confidence(resume_text)
        
        print(f"📊 ANALYSIS RESULTS:")
        print(f"Total skills found: {len(extracted_skills)}")
        
        # Show top skills
        extracted_skills.sort(key=lambda x: x['confidence'], reverse=True)
        print(f"\nTop 15 skills by confidence:")
        for i, skill in enumerate(extracted_skills[:15], 1):
            print(f"{i:2d}. {skill['name']:<25} {skill['confidence']:.2f} ({skill['skill_level']})")
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    # Test with sample resume
    test_resume_analysis()
    
    # Test with actual file if provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print("\n" + "="*80 + "\n")
        test_with_file(file_path)
    else:
        print(f"\n💡 TIP: You can also test with a real resume file:")
        print(f"python test_resume_analysis.py path/to/your/resume.pdf")
        
        # Check if there are any resume files in the resumes folder
        resume_dir = "resumes"
        if os.path.exists(resume_dir):
            resume_files = [f for f in os.listdir(resume_dir) if f.endswith(('.pdf', '.docx', '.txt'))]
            if resume_files:
                print(f"\n📁 Found resume files in '{resume_dir}' folder:")
                for file in resume_files:
                    print(f"   - {file}")
                print(f"\nTo test with one of these files, run:")
                print(f"python test_resume_analysis.py resumes/{resume_files[0]}") 