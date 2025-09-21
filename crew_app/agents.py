from crewai import Agent
import os


MODEL = "gpt-4o-mini"

# Agent 1: Parses resume text and cleans it for LLM consumption
def build_parser_agent():
    return Agent(
        role="Resume Parsing Specialist",
        goal="Extract clean, structured text from a resume suitable for ATS optimization.",
        backstory=(
            "You efficiently clean resume text by removing artifacts and normalizing formatting. "
            "Focus on speed and accuracy - preserve all important content while removing noise."
        ),
        model=MODEL,
        temperature=0.0,
        max_iter=1,
        max_execution_time=120
    )

# Agent 2: ATS Optimizer — rewrites resume tailored to job
def build_ats_writer_agent():
    return Agent(
        role="ATS Optimization Writer",
        goal="Create a high-scoring ATS-optimized resume that matches job requirements perfectly.",
        backstory=(
            "You are an expert at transforming resumes into ATS-friendly formats that score 80+ points. "
            "You strategically place keywords, use strong action verbs, and quantify all achievements. "
            "You work quickly and deliver results that pass ATS systems."
        ),
        model=MODEL,
        temperature=0.3,
        max_iter=1,
        max_execution_time=120
    )

# Agent 3: Evaluator — scores ATS readiness & highlights gaps
def build_evaluator_agent():
    return Agent(
        role="ATS Evaluator",
        goal="Provide accurate ATS scores and actionable improvement recommendations.",
        backstory=(
            "You are a precise ATS scoring expert who quickly identifies gaps and provides specific, "
            "actionable recommendations. You focus on keyword density, section structure, and measurable achievements."
        ),
        model=MODEL,
        temperature=0.0,
        max_iter=1,
        max_execution_time=120
    )

# Agent 4: Bullet Refiner — polishes bullets with metrics & action verbs
def build_refiner_agent():
    return Agent(
        role="Bullet Point Refiner",
        goal="Transform bullet points into high-impact, ATS-optimized statements with strong metrics.",
        backstory="You excel at creating powerful bullet points that combine action verbs, specific achievements, and quantified results. You work efficiently to maximize impact.",
        model=MODEL,
        temperature=0.2,
        max_iter=1,
        max_execution_time=120
    )
