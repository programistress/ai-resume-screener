import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_screener.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_job_analysis():
    from resume_screening.utils.analyze_job_requirements import analyze_job_requirements
    
    job_desc = """
    Typical Day in Role

    Implementing and automating models developed by the product team.
    Generating statistical models based on use cases and ensuring correct correlation analysis for clients (e.g., identifying similar clients and generating insights based on similarities).
    Turning data into code to help client's Capital Market deliver real-time analytics to customers.
    Supporting the transition from batch processing to real-time insights, helping build the framework and engine for this initiative.


    Soft Skills: Strong Communication, Stakeholder Management, Time Management, Adaptability, Problem Solving

    Candidate Requirements/Must-Have Skills:

    7+ years of experience in a data science role
    Expert-level Python skills (pandas, NumPy, matplotlib, requests, scikit-learn)
    Strong experience in machine learning frameworks such as PyTorch (or Keras, TensorFlow, Apache Spark)
    Hands-on experience optimizing quantitative models
    Deep knowledge of mathematics and statistics
    Experience in data engineering for distributed stream processing
    Previous exposure to AI tools and technologies
    Strong communication skills, ability to work with cross functional teams, ability to translate technical terminology, strong initiative, team first mentality, creative and curious to learn. 

    Nice-to-Have Skills

    Experience in banking or capital markets

    Education

    Bachelor's degree in a technical field such as computer science or computer engineering. 


    Best vs. Average Candidate

    The ideal candidate will possess strong soft skills and a can-do attitude. Meeting 80% of the technical skills and 20% of the domain knowledge would be ideal. Experience in banking or capital markets is a strong plus.
        
    """   

    requirements = analyze_job_requirements(job_desc)

    print("Important Terms:")
    for term in requirements['important_terms']:
        print(f"  - {term}")
    
    print("\nKey Phrases:")
    for phrase in requirements['key_phrases']:
        print(f"  - {phrase}")
    
    return requirements

if __name__ == "__main__":
    test_job_analysis()