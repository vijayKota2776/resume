from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import datetime
from pydantic import BaseModel
from google.cloud.firestore_v1.base_query import FieldFilter
from .. import models, database, auth

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
def register(user: UserCreate):
    users_ref = database.db.collection('users')
    existing = users_ref.where(filter=FieldFilter('email', '==', user.email)).limit(1).get()
    
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

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_ref = database.db.collection('users')
    query = users_ref.where(filter=FieldFilter('email', '==', form_data.username)).limit(1).get()
    
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
