from crewai import Task

def parse_resume_task(agent, raw_resume_text):
    # Truncate if too long
    truncated_text = raw_resume_text[:1500] + "..." if len(raw_resume_text) > 1500 else raw_resume_text
    
    return Task(
        description=(
            f"Clean this resume text quickly:\n\n{truncated_text}\n\n"
            "Remove artifacts, normalize bullets to '-', keep all content. Be fast and direct."
        ),
        agent=agent,
        expected_output=("Clean resume text with proper structure.")
    )

def rewrite_for_ats_task(agent, cleaned_resume_text, job_title, job_description):
    # Truncate inputs if too long
    truncated_resume = cleaned_resume_text[:1200] + "..." if len(cleaned_resume_text) > 1200 else cleaned_resume_text
    truncated_jd = job_description[:300] + "..." if len(job_description) > 300 else job_description
    
    return Task(
        description=(
            f"Rewrite resume for {job_title}:\n\n"
            f"JOB: {truncated_jd}\n\n"
            f"RESUME: {truncated_resume}\n\n"
            "Match keywords, use action verbs, add metrics. Target 80+ ATS score. Be direct and fast."
        ),
        agent=agent,
        expected_output="ATS-optimized resume with keyword placement and metrics."
    )

def refine_bullets_task(agent, rewritten_resume_text):
    truncated_text = rewritten_resume_text[:1000] + "..." if len(rewritten_resume_text) > 1000 else rewritten_resume_text
    
    return Task(
        description=(
            f"Polish these bullets with action verbs and metrics:\n\n{truncated_text}\n\n"
            "Add strong verbs and numbers. Be fast and direct."
        ),
        agent=agent,
        expected_output="Resume with enhanced bullet points and metrics."
    )

def evaluate_ats_task(agent, final_resume_text, job_title, job_description):
    truncated_resume = final_resume_text[:800] + "..." if len(final_resume_text) > 800 else final_resume_text
    truncated_jd = job_description[:200] + "..." if len(job_description) > 200 else job_description
    
    return Task(
        description=(
            f"Score this resume for {job_title}:\n\n"
            f"JOB: {truncated_jd}\n\n"
            f"RESUME: {truncated_resume}\n\n"
            "Rate 1-5: keywords, structure, metrics, verbs, format. Return JSON with overall_score (0-100), breakdown, missing_keywords, quick_wins."
        ),
        agent=agent,
        expected_output="JSON evaluation with scores and recommendations."
    )
