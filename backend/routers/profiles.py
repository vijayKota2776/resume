from fastapi import APIRouter, Depends, HTTPException
import datetime
from pydantic import BaseModel
from typing import Dict, Any
from .. import models, database, auth

router = APIRouter()

class ProfileCreate(BaseModel):
    parsed_data: Dict[str, Any]

@router.post("/profile/manual")
def create_manual_profile(
    profile_data: ProfileCreate,
    current_user: models.User = Depends(auth.get_current_user)
):
    profiles_ref = database.db.collection('profiles')
    profile_doc = profiles_ref.document(current_user.id)
    profile_doc.set({
        "user_id": current_user.id,
        "parsed_data": profile_data.parsed_data,
        "updated_at": datetime.datetime.utcnow().isoformat()
    })
    return {"message": "Profile created successfully", "profile_id": current_user.id}

@router.get("/profile")
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    profiles_ref = database.db.collection('profiles')
    profile_doc = profiles_ref.document(current_user.id).get()
    
    if not profile_doc.exists:
        return {"has_profile": False}
        
    return {"has_profile": True, "data": profile_doc.to_dict().get("parsed_data", {})}
