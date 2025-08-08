def match_skills(user_skills, job_list):
    matched_jobs = []
    for job in job_list:
        for skill in user_skills.split(','):
            if skill.lower().strip() in job.lower():
                matched_jobs.append(job)
                break
    return list(set(matched_jobs))
