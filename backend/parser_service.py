import os
import json
import requests
from typing import Dict, Any

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

PARSE_SYSTEM_PROMPT = """Extract the following structured JSON from this resume: full_name, email, phone, summary, work_experience (list with company, role, dates, bullet_points), education (list with degree, institution, year), and skills (list). Return ONLY valid JSON."""

def parse_resume_text(raw_text: str) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": raw_text}
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    else:
        raise Exception(f"Failed to parse resume: {response.text}")
