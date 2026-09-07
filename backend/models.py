from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    created_at: str

class Profile(BaseModel):
    id: str
    user_id: str
    parsed_data: Dict[str, Any]
    updated_at: str

class ResumeVersion(BaseModel):
    id: str
    base_profile_id: str
    application_id: Optional[str] = None
    tailored_data: Dict[str, Any]
    latex_content: Optional[str] = None
    pdf_url: Optional[str] = None
    version: int = 1
    created_at: str

class Application(BaseModel):
    id: str
    user_id: str
    company_name: str
    job_title: str
    job_description: str
    ats_score: Optional[int] = None
    status: str = "draft"
    applied_at: str
