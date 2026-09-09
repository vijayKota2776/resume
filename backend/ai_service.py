import os
import json
import google.generativeai as genai
from typing import Dict, Any

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are a professional resume optimizer. You will be given:
1. A user's full profile in JSON format: [name, contact, summary, work_experience (list with company, role, dates, bullet points), education, skills, projects, certifications].
2. A Job Description (JD).
Your goal is to tailor the user's resume JSON to best match the JD without making up fake experience.
- Rewrite the `summary` to highlight relevant skills.
- Rewrite `bullet_points` in `work_experience` to emphasize matching keywords from the JD.
- Reorder `skills` to put matching ones first.
IMPORTANT: You MUST return the ENTIRE JSON profile. Do NOT delete any sections, arrays, or fields (like company, role, dates, education, etc.) even if you don't edit them. Return ONLY the complete, modified JSON profile."""

REFINE_SYSTEM_PROMPT = """You are a professional resume editor.
You will receive the original Job Description, the current JSON version of the tailored resume, and a piece of feedback from the user.
Your job is to update the JSON resume according to the user's feedback, while keeping it tailored to the JD.
IMPORTANT: You MUST return the ENTIRE JSON profile. Do NOT delete any sections, arrays, or fields (like company, role, dates, education, etc.) even if you don't edit them. Return ONLY the complete, modified JSON profile."""

def tailor_resume(profile_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        import copy
        mock = copy.deepcopy(profile_data)
        if "summary" in mock:
            mock["summary"] = "[MOCK TAILORED] " + mock["summary"]
        if "work_experience" in mock and len(mock["work_experience"]) > 0:
            if "bullet_points" not in mock["work_experience"][0]:
                mock["work_experience"][0]["bullet_points"] = []
            mock["work_experience"][0]["bullet_points"].append("MOCK: Increased scalability by 200%.")
        return mock

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.6-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"{SYSTEM_PROMPT}\n\nUser Profile JSON:\n{json.dumps(profile_data, indent=2)}\n\nJob Description:\n{job_description}"
    response = model.generate_content(prompt)
    
    return json.loads(response.text)

def refine_resume(current_resume: Dict[str, Any], feedback: str, jd_text: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        import copy
        mock = copy.deepcopy(current_resume)
        mock["summary"] = "[MOCK REFINED] " + mock.get("summary", "") + f" (Feedback: {feedback})"
        return mock

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.6-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"{REFINE_SYSTEM_PROMPT}\n\nOriginal Job Description Context:\n{jd_text}\n\nCurrent Resume JSON:\n{json.dumps(current_resume, indent=2)}\n\nUser Feedback:\n{feedback}"
    response = model.generate_content(prompt)
    
    return json.loads(response.text)
