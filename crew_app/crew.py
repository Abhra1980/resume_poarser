import os
from crewai import Crew, Process
from .agents import (
    build_parser_agent, build_ats_writer_agent,
    build_evaluator_agent, build_refiner_agent
)
from .tasks import (
    parse_resume_task, rewrite_for_ats_task,
    evaluate_ats_task, refine_bullets_task
)

def build_crew(raw_resume_text: str, job_title: str, job_description: str):
    parser = build_parser_agent()
    writer = build_ats_writer_agent()
    refiner = build_refiner_agent()
    evaluator = build_evaluator_agent()

    t_parse = parse_resume_task(parser, raw_resume_text)
    # these are placeholders; we'll stitch later after parse result is known
    t_rewrite = rewrite_for_ats_task(writer, "{CLEANED_RESUME}", job_title, job_description)
    t_refine = refine_bullets_task(refiner, "{REWRITTEN_RESUME}")
    t_eval = evaluate_ats_task(evaluator, "{FINAL_RESUME}", job_title, job_description)

    crew = Crew(
        agents=[parser, writer, refiner, evaluator],
        tasks=[t_parse, t_rewrite, t_refine, t_eval],
        process=Process.sequential,
        verbose=True
    )
    return crew

def run_pipeline(raw_resume_text: str, job_title: str, job_description: str):
    # Build agents
    parser = build_parser_agent()
    writer = build_ats_writer_agent()
    refiner = build_refiner_agent()
    evaluator = build_evaluator_agent()

    # Create tasks
    t_parse = parse_resume_task(parser, raw_resume_text)
    
    # Build and run crew for parsing
    parse_crew = Crew(
        agents=[parser],
        tasks=[t_parse],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute parsing
    parse_result = parse_crew.kickoff()
    cleaned = str(parse_result).strip()

    # Create rewrite task with cleaned resume
    t_rewrite = rewrite_for_ats_task(writer, cleaned, job_title, job_description)
    rewrite_crew = Crew(
        agents=[writer],
        tasks=[t_rewrite],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute rewriting
    rewrite_result = rewrite_crew.kickoff()
    rewritten = str(rewrite_result).strip()

    # Create refine task with rewritten resume
    t_refine = refine_bullets_task(refiner, rewritten)
    refine_crew = Crew(
        agents=[refiner],
        tasks=[t_refine],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute refining
    refine_result = refine_crew.kickoff()
    final_resume = str(refine_result).strip()

    # Create evaluation task with final resume
    t_eval = evaluate_ats_task(evaluator, final_resume, job_title, job_description)
    eval_crew = Crew(
        agents=[evaluator],
        tasks=[t_eval],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute evaluation
    eval_result = eval_crew.kickoff()
    evaluation = str(eval_result).strip()

    return cleaned, rewritten, final_resume, evaluation
