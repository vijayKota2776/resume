import requests

BASE_URL = "http://localhost:8000"
email = "frontend_test@example.com"
password = "password123"

# Register
res = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
if res.status_code == 200 or res.status_code == 400:
    # Login to get token
    res = requests.post(f"{BASE_URL}/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    
    # Create profile
    profile_data = {
        "summary": "Software Engineer with 5 years of experience",
        "work_experience": [
            {
                "company": "Tech Corp",
                "role": "Backend Developer",
                "dates": "2020 - Present",
                "bullet_points": ["Developed APIs", "Scaled databases"]
            }
        ],
        "education": [{"degree": "B.S. CS", "institution": "University", "year": "2020"}],
        "skills": ["Python", "FastAPI", "React"]
    }
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/profile/manual", json={"parsed_data": profile_data}, headers=headers)
    print("Seed complete")
