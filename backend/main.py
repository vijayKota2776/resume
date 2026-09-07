from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any, Optional
import datetime
from google.cloud import firestore

from . import models, database, auth, parsing, ai_service, latex_service, parser_service

app = FastAPI(title="ResumeTailor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileCreate(BaseModel):
    parsed_data: Dict[str, Any]

class ParseTextRequest(BaseModel):
    text: str

class TailorRequest(BaseModel):
    jd_text: str

class GeneratePDFRequest(BaseModel):
    version_id: str
    template: str = "modern"

class RefineRequest(BaseModel):
    current_resume_json: Dict[str, Any]
    feedback: str
    jd_text: str

@app.post("/register", response_model=Token)
def register(user: UserCreate):
    users_ref = database.db.collection('users')
    existing = users_ref.where('email', '==', user.email).limit(1).get()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    _, doc_ref = users_ref.add(new_user_data)
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_ref = database.db.collection('users')
    query = users_ref.where('email', '==', form_data.username).limit(1).get()
    
    if not query:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    user_data = query[0].to_dict()
    if not auth.verify_password(form_data.password, user_data['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user_data['email']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/parse-resume")
async def parse_resume_endpoint(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user)
):
    content = await file.read()
    try:
        text = parsing.extract_text_from_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        parsed_data = parser_service.parse_resume_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse with AI: {str(e)}")
    
    return {"message": "Resume parsed successfully", "data": parsed_data}

@app.post("/api/parse-resume-text")
async def parse_resume_text_endpoint(
    request: ParseTextRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        parsed_data = parser_service.parse_resume_text(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse with AI: {str(e)}")
    
    return {"message": "Text parsed successfully", "data": parsed_data}

@app.post("/profile/manual")
def create_manual_profile(
    profile_data: ProfileCreate,
    current_user: models.User = Depends(auth.get_current_user)
):
    profiles_ref = database.db.collection('profiles')
    # Store one profile per user for simplicity, using user_id as doc id
    profile_doc = profiles_ref.document(current_user.id)
    profile_doc.set({
        "user_id": current_user.id,
        "parsed_data": profile_data.parsed_data,
        "updated_at": datetime.datetime.utcnow().isoformat()
    })
    return {"message": "Profile created successfully", "profile_id": current_user.id}

@app.post("/api/tailor-resume")
def api_tailor_resume(
    request: TailorRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    profile_doc = database.db.collection('profiles').document(current_user.id).get()
    if not profile_doc.exists:
        raise HTTPException(status_code=404, detail="No base profile found. Please create one first.")
    
    profile_data = profile_doc.to_dict()
    
    try:
        tailored_data = ai_service.tailor_resume(profile_data['parsed_data'], request.jd_text)
        
        versions_ref = database.db.collection('resume_versions')
        created_at = datetime.datetime.utcnow().isoformat()
        
        _, doc_ref = versions_ref.add({
            "base_profile_id": current_user.id,
            "tailored_data": tailored_data,
            "version": 1,
            "created_at": created_at
        })
        
        return {"id": doc_ref.id, "version": 1, "data": tailored_data, "created_at": created_at}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-pdf")
def api_generate_pdf(
    request: GeneratePDFRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user)
):
    version_doc = database.db.collection('resume_versions').document(request.version_id).get()
    if not version_doc.exists:
        raise HTTPException(status_code=404, detail="Version not found.")
        
    version_data = version_doc.to_dict()
    if version_data['base_profile_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized.")
        
    try:
        pdf_bytes = latex_service.generate_pdf(version_data['tailored_data'], request.template)
        
        import tempfile
        import os
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, 'wb') as f:
            f.write(pdf_bytes)
            
        def cleanup(path):
            os.unlink(path)
            
        background_tasks.add_task(cleanup, temp_path)
        
        return FileResponse(
            path=temp_path, 
            media_type="application/pdf", 
            filename=f"Tailored_Resume_v{version_data.get('version', 1)}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refine-resume")
def api_refine_resume(
    request: RefineRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    profile_doc = database.db.collection('profiles').document(current_user.id).get()
    if not profile_doc.exists:
        raise HTTPException(status_code=404, detail="No profile found.")
        
    try:
        refined_data = ai_service.refine_resume(request.current_resume_json, request.feedback, request.jd_text)
        
        versions_ref = database.db.collection('resume_versions')
        # Get latest version number
        query = versions_ref.where('base_profile_id', '==', current_user.id).order_by('version', direction=firestore.Query.DESCENDING).limit(1).get()
        
        new_v = (query[0].to_dict().get('version', 1) + 1) if query else 2
        created_at = datetime.datetime.utcnow().isoformat()
        
        _, doc_ref = versions_ref.add({
            "base_profile_id": current_user.id,
            "tailored_data": refined_data,
            "version": new_v,
            "created_at": created_at
        })
        
        return {"id": doc_ref.id, "version": new_v, "data": refined_data, "created_at": created_at}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resume-versions")
def get_resume_versions(current_user: models.User = Depends(auth.get_current_user)):
    versions_ref = database.db.collection('resume_versions')
    query = versions_ref.where('base_profile_id', '==', current_user.id).order_by('created_at', direction=firestore.Query.DESCENDING).get()
    
    results = []
    for doc in query:
        v = doc.to_dict()
        results.append({
            "id": doc.id,
            "version": v.get('version', 1),
            "data": v.get('tailored_data', {}),
            "created_at": v.get('created_at', '')
        })
    return results
