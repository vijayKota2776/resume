import os
import json
import google.generativeai as genai
from typing import Dict, Any

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

PARSE_SYSTEM_PROMPT = """Extract the following structured JSON from this resume: full_name, email, phone, summary, work_experience (list with company, role, dates, bullet_points), education (list with degree, institution, year), and skills (list). Return ONLY valid JSON."""

def parse_resume_text(raw_text: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.6-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"{PARSE_SYSTEM_PROMPT}\n\nResume Text:\n{raw_text}"
    response = model.generate_content(prompt)
    
    return json.loads(response.text)
