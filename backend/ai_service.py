import os
import json
import requests
from typing import Dict, Any

# We can use the OpenAI API or Gemini API. Here is an example using OpenAI structure.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

SYSTEM_PROMPT = """You are a professional resume optimizer. You will be given:
1. A user's full profile in JSON format: [name, contact, summary, work_experience (list with company, role, dates, bullet points), education, skills, projects, certifications].
2. A job description (JD) text.

Your tasks:
- Extract the top 5-7 keywords and required skills from the JD.
- Compare them with the user's skills and experience.
- Rewrite the user's work experience bullet points and summary to emphasize the most relevant achievements, using strong action verbs and quantifiable results.
- IMPORTANT: Never add fake experience, degrees, or skills. Only rephrase what is already there, and if a required skill is missing, you may suggest adding a "Relevant Coursework" or "Certifications" section only if the user already has something related.
- Output the revised resume in structured JSON with fields: summary, work_experience (list of updated bullet points), skills (re-ordered to highlight JD-relevant ones), and optionally a new "ATS Keywords" section.
- Also return a list of matched keywords and a count of missing critical skills for the ATS score.

Be concise and professional.
"""

def tailor_resume(profile_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Calls the LLM API to tailor the resume based on the JD.
    """
    if not OPENAI_API_KEY:
        # Return mock tailored data for testing without API key
        import copy
        mock = copy.deepcopy(profile_data)
        mock["summary"] = "MOCK-TAILORED: " + mock.get("summary", "")
        mock["ats_score"] = 95
        mock["matched_keywords"] = ["Python", "FastAPI", "React"]
        mock["missing_keywords"] = ["AWS"]
        if "work_experience" in mock and len(mock["work_experience"]) > 0:
            mock["work_experience"][0]["bullet_points"].append("MOCK: Increased scalability by 200%.")
        return mock

    prompt_content = f"User Profile JSON:\n{json.dumps(profile_data, indent=2)}\n\nJob Description:\n{job_description}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",  # or gpt-3.5-turbo depending on preference
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    else:
        raise Exception(f"Failed to generate tailored resume: {response.text}")

REFINE_SYSTEM_PROMPT = """You are a resume editor. You have the current resume JSON and the user's feedback. Apply the changes strictly to the content requested. Never change facts or invent new ones. Only rephrase or restructure based on the instruction. Return the updated JSON in the exact same schema.
"""

def refine_resume(current_resume: Dict[str, Any], feedback: str, jd_text: str) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        import copy
        mock = copy.deepcopy(current_resume)
        mock["summary"] = "[MOCK REFINED] " + mock.get("summary", "") + f" (Feedback: {feedback})"
        return mock

    prompt_content = f"Original Job Description Context:\n{jd_text}\n\nCurrent Resume JSON:\n{json.dumps(current_resume, indent=2)}\n\nUser Feedback:\n{feedback}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": REFINE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    else:
        raise Exception(f"Failed to refine resume: {response.text}")
