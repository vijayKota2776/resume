import requests
import time
import os

BASE_URL = "http://localhost:8000"

def test_flow():
    print("1. Registering user...")
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    res = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
    if res.status_code != 200:
        print("Registration failed:", res.text)
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Registration successful!")

    print("2. Creating manual profile...")
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
    res = requests.post(f"{BASE_URL}/profile/manual", json={"parsed_data": profile_data}, headers=headers)
    if res.status_code != 200:
        print("Profile creation failed:", res.text)
        return
    print("Profile created!")

    print("3. Tailoring resume... (this might take a few seconds due to AI)")
    jd_text = "Looking for a Python developer with FastAPI experience to build scalable backends."
    res = requests.post(f"{BASE_URL}/api/tailor-resume", json={"jd_text": jd_text}, headers=headers)
    if res.status_code != 200:
        print("Tailor failed:", res.text)
        return
    version_id = res.json()["id"]
    print("Tailor successful! Version ID:", version_id)

    print("4. Generating PDF...")
    res = requests.post(f"{BASE_URL}/api/generate-pdf", json={"version_id": version_id, "template": "classic"}, headers=headers)
    if res.status_code != 200:
        print("PDF generation failed:", res.text)
        return
    
    with open("test_output.pdf", "wb") as f:
        f.write(res.content)
    print("PDF generated and saved to test_output.pdf! File size:", os.path.getsize("test_output.pdf"), "bytes")
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_flow()
