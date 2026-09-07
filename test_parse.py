import requests

BASE_URL = "http://localhost:8000"
email = "firebase_test2@example.com"
password = "password123"

# Register
reg_res = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
print("Register Status:", reg_res.status_code)
print("Register Text:", reg_res.text)

# Login
res = requests.post(f"{BASE_URL}/login", data={"username": email, "password": password})
print("Login Status:", res.status_code)
print("Login Text:", res.text)
