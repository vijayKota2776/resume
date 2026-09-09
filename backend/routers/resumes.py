from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks
import datetime
from pydantic import BaseModel
from typing import Dict, Any
from google.cloud import firestore
import tempfile
import os

from .. import models, database, auth, parsing, ai_service, latex_service, parser_service

router = APIRouter()

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

@router.post("/api/parse-resume")
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

@router.post("/api/parse-resume-text")
async def parse_resume_text_endpoint(
    request: ParseTextRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        parsed_data = parser_service.parse_resume_text(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse with AI: {str(e)}")
    
    return {"message": "Text parsed successfully", "data": parsed_data}

@router.post("/api/tailor-resume")
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

@router.post("/api/generate-pdf")
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

@router.post("/api/refine-resume")
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
        query = versions_ref.where(filter=firestore.FieldFilter('base_profile_id', '==', current_user.id)).get()
        
        max_version = 0
        for doc in query:
            v = doc.to_dict().get('version', 0)
            if v > max_version:
                max_version = v
                
        new_v = max_version + 1 if max_version > 0 else 2
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

@router.get("/api/resume-versions")
def get_resume_versions(current_user: models.User = Depends(auth.get_current_user)):
    versions_ref = database.db.collection('resume_versions')
    query = versions_ref.where(filter=firestore.FieldFilter('base_profile_id', '==', current_user.id)).get()
    
    results = []
    for doc in query:
        v = doc.to_dict()
        results.append({
            "id": doc.id,
            "version": v.get('version', 1),
            "data": v.get('tailored_data', {}),
            "created_at": v.get('created_at', '')
        })
    
    # Sort in memory descending by created_at to avoid requiring a composite index in Firestore
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results
