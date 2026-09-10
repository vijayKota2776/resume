import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import database  # Initialize database

from .routers import auth, profiles, resumes

app = FastAPI(title="ResumeTailor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(profiles.router, tags=["Profiles"])
app.include_router(resumes.router, tags=["Resumes"])
