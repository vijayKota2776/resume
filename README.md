# ResumeTailor 🤖📄

![Live Demo](https://img.shields.io/badge/Live_Demo-Online-success?style=for-the-badge) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black) ![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

ResumeTailor is an AI-powered full-stack application designed to help job seekers instantly customize and tailor their resumes for specific job descriptions. By leveraging Google's Gemini AI, the application maps your master profile against target job descriptions and generates highly optimized, ATS-friendly LaTeX PDF resumes in seconds.

**Live Application:** [https://resume-nu-ten-12.vercel.app](https://resume-nu-ten-12.vercel.app)

---

## 🌟 Key Features

- **Automated Resume Parsing:** Upload an existing PDF or DOCX resume, and the AI will automatically extract and parse your work experience, education, and skills into a structured master profile.
- **AI-Powered Tailoring:** Paste a job description (JD), and the Gemini AI will rewrite and reorder your bullet points to perfectly align with the JD while maintaining strict factual accuracy.
- **Interactive Refinement:** Not happy with a specific bullet point? Use the built-in AI chat interface to ask for revisions (e.g., "Make the summary more impactful" or "Highlight my leadership skills more").
- **Version Control:** Every tailored resume is saved as a new version. Easily browse, revert, and download previous iterations of your tailored resumes.
- **High-Quality PDF Exports:** Resumes are dynamically rendered using Jinja2 and LaTeX, exporting beautiful, professional, ATS-compliant PDFs.
- **Secure Authentication:** JWT-based user authentication ensuring your master profile and tailored resumes are kept private and secure.

---

## 🛠️ Technology Stack

**Frontend (Client)**
- **React 18** (Vite)
- **Tailwind CSS** (for responsive, modern styling)
- **React Router v6** (for SPA navigation)
- **Axios** (for API communication with interceptors for seamless auth handling)
- **Lucide React** (for modern SVG icons)

**Backend (Server)**
- **FastAPI** (High-performance Python API framework)
- **Google Generative AI SDK** (Integration with Gemini Pro models)
- **Jinja2** (for templating LaTeX `.tex` files)
- **PyJWT & Passlib** (for secure password hashing and JWT issuance)
- **Python-Multipart** (for handling file uploads)

**Database & Infrastructure**
- **Google Cloud Firestore / Firebase** (NoSQL Document Database for profiles and version history)
- **Vercel** (Frontend Hosting)
- **Render** (Backend Hosting)

---

## 🚀 Local Setup & Installation

To run this project locally on your machine, you'll need Node.js, Python 3.9+, and a Firebase Service Account key.

### 1. Clone the repository
```bash
git clone https://github.com/vijayKota2776/resume.git
cd resume
```

### 2. Backend Setup
Navigate to the backend directory and set up your Python environment:
```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

**Environment Variables:** 
Create a `.env` file in the root directory and add the following:
```env
GEMINI_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_random_jwt_secret_key
# FIREBASE_CREDENTIALS=... (Only needed in production if not using the local JSON file)
```
*Note: For local development, ensure your Firebase Service Account JSON file is placed in the root directory and named exactly as specified in `backend/database.py`.*

**Start the Backend Server:**
```bash
uvicorn backend.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and start the Vite dev server:
```bash
cd frontend-react
npm install
npm run dev
```
The React app will be available at `http://localhost:5173`.

---

## ☁️ Deployment

This application is configured for easy deployment on modern cloud platforms.

- **Frontend (Vercel):** Set the Root Directory to `frontend-react` and ensure the `VITE_API_URL` environment variable is set to your live backend URL.
- **Backend (Render):** Set the Root Directory to the repository root (leave blank), use `pip install -r backend/requirements.txt` for the build command, and `uvicorn backend.main:app --host 0.0.0.0 --port 10000` for the start command. Ensure you add `GEMINI_API_KEY`, `SECRET_KEY`, and `FIREBASE_CREDENTIALS` (raw JSON string) as environment variables in the Render dashboard.

---


