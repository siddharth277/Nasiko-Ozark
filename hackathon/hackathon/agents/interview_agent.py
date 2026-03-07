"""
Interview Agent - Generates personalized interview questions
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_interview_questions(jd: str, candidate_summary: str, candidate_skills: list, candidate_projects: list) -> str:
    """Generate 5 tailored interview questions based on JD and Resume."""
    
    # Format projects properly without backslash in f-string
    projects_text = 'None provided'
    if candidate_projects:
        projects_list = '\n- '.join(candidate_projects)
        projects_text = f'- {projects_list}'
    
    prompt = f"""You are an expert technical recruiter preparing an interviewer for an upcoming interview.
Based on the provided Job Description and Candidate Profile, generate exactly 5 interview questions.
Make them highly personalized. Do not ask generic questions like "What are your strengths?".
Instead, ask about specific gaps between their skills and the JD, or ask them to elaborate on a specific project they listed.

JOB DESCRIPTION:
{jd[:1500]}

CANDIDATE SUMMARY:
{candidate_summary}

CANDIDATE SKILLS:
{', '.join(candidate_skills)}

CANDIDATE PROJECTS:
{projects_text}

Format the output as a Markdown numbered list, with a brief 1-sentence explanation of *why* the interviewer should ask this question.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Interview questions error: {e}")
        return "Failed to generate interview questions. Please try again."
