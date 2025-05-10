from resume_screening.models import Resume, JobDescription, ResumeSkill, JobSkill, Skill

def calculate_skill_match(resume_id, job_id):
    """
    calculating match percentage resume to jobdesc
    args: resume id, jobdesc id
    returns: dictionary: match percentage, matching skills, missing skills
    """
    
    #getting resume skills and job skills ids

    resume_skills = ResumeSkill.objects.filter(resume_id=resume_id)
    resume_skill_ids = {rs.skill_id for rs in resume_skills}
    
    job_skills = JobSkill.objects.filter(job_id=job_id)
    job_skill_ids = {js.skill_id for js in job_skills}

    matching_skills = resume_skill_ids.intersection(job_skill_ids)
    missing_skills = job_skill_ids - resume_skill_ids
    
    # calculating percentage score like (6 / 10) * 100 = 60% and check to not divide by 0
    if len(job_skill_ids) > 0:
        match_percentage = (len(matching_skills) / len(job_skill_ids)) * 100
    else:
        match_percentage = 0
    
    #skills info
    matching_skill_details = Skill.objects.filter(id__in=matching_skills)
    missing_skill_details = Skill.objects.filter(id__in=missing_skills)
    
    return {
        'match_percentage': match_percentage,
        'matching_skills': list(matching_skill_details.values('name', 'category', 'subcategory')),
        'missing_skills': list(missing_skill_details.values('name', 'category', 'subcategory'))
    }