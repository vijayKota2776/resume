import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="ResumeTailor", layout="wide")

def login_user(email, password):
    response = requests.post(f"{BACKEND_URL}/login", data={"username": email, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def register_user(email, password):
    response = requests.post(f"{BACKEND_URL}/register", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def upload_resume(token, file):
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (file.name, file, file.type)}
    response = requests.post(f"{BACKEND_URL}/api/parse-resume", headers=headers, files=files)
    return response

def submit_manual_profile(token, data):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BACKEND_URL}/profile/manual", headers=headers, json={"parsed_data": data})
    return response

def generate_tailored_resume(token, jd_text):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BACKEND_URL}/api/tailor-resume", headers=headers, json={"jd_text": jd_text})
    return response

def generate_pdf(token, version_id, template_choice):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(
        f"{BACKEND_URL}/api/generate-pdf",
        headers=headers,
        json={"version_id": version_id, "template": template_choice}
    )
    return response

def get_versions(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/api/resume-versions", headers=headers)
    return response

def refine_resume_api(token, current_json, feedback, jd_text):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(
        f"{BACKEND_URL}/api/refine-resume",
        headers=headers,
        json={"current_resume_json": current_json, "feedback": feedback, "jd_text": jd_text}
    )
    return response

if "token" not in st.session_state:
    st.session_state.token = None
if "tailored_data" not in st.session_state:
    st.session_state.tailored_data = None
if "current_version_id" not in st.session_state:
    st.session_state.current_version_id = None
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "parsed_profile_data" not in st.session_state:
    st.session_state.parsed_profile_data = {}

if not st.session_state.token:
    st.title("Welcome to ResumeTailor")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            token = login_user(email, password)
            if token:
                st.session_state.token = token
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    with tab2:
        st.subheader("Sign Up")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Sign Up"):
            token = register_user(new_email, new_password)
            if token:
                st.session_state.token = token
                st.success("Registered successfully!")
                st.rerun()
            else:
                st.error("Registration failed. Email might already be taken.")
else:
    st.sidebar.title("ResumeTailor")
    st.sidebar.write("Logged in.")
    
    # Version History
    st.sidebar.subheader("Version History")
    if st.sidebar.button("Refresh History"):
        st.rerun()
        
    versions_res = get_versions(st.session_state.token)
    if versions_res and versions_res.status_code == 200:
        versions = versions_res.json()
        if not versions:
            st.sidebar.write("No tailored versions yet.")
        for v in versions:
            if st.sidebar.button(f"Version {v['version']} - {v['created_at'][:16].replace('T', ' ')}", key=f"ver_{v['id']}"):
                st.session_state.tailored_data = v['data']
                st.session_state.current_version_id = v['id']
                st.rerun()
                
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.tailored_data = None
        st.session_state.current_version_id = None
        st.session_state.jd_text = ""
        st.rerun()

    st.title("Create your Profile")
    st.write("To tailor your resume, we first need your base profile. You can either upload an existing resume or fill out the form manually.")
    
    tab1, tab2, tab3 = st.tabs(["Upload Resume", "Manual Entry", "Tailor Resume"])
    
    with tab1:
        st.subheader("Upload Existing Resume")
        uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
        if st.button("Upload and Parse"):
            if uploaded_file is not None:
                with st.spinner("Parsing resume..."):
                    res = upload_resume(st.session_state.token, uploaded_file)
                    if res.status_code == 200:
                        parsed_data = res.json()["data"]
                        st.session_state.parsed_profile_data = parsed_data
                        st.success("Resume parsed successfully! Switch to the 'Manual Entry' tab to review and save.")
                        st.json(parsed_data)
                    else:
                        st.error(f"Failed to upload: {res.text}")
            else:
                st.warning("Please select a file first.")
                
    with tab2:
        st.subheader("Manual Profile Entry")
        
        parsed = st.session_state.parsed_profile_data
        default_summary = parsed.get("summary", "")
        
        # Formatting experience list into a text blob for the simple textarea
        default_exp = ""
        for exp in parsed.get("work_experience", []):
            default_exp += f"{exp.get('role', '')} at {exp.get('company', '')}: {', '.join(exp.get('bullet_points', []))}\n"
            
        default_edu = ", ".join([f"{e.get('degree', '')} {e.get('institution', '')}" for e in parsed.get("education", [])])
        default_skills = ", ".join(parsed.get("skills", []))

        with st.form("manual_profile_form"):
            summary = st.text_area("Professional Summary", value=default_summary)
            experience = st.text_area("Experience (e.g., Job Title at Company: Description)", value=default_exp)
            education = st.text_input("Education (e.g., B.S. Computer Science)", value=default_edu)
            skills = st.text_input("Skills (comma-separated)", value=default_skills)
            
            submitted = st.form_submit_button("Save Profile")
            if submitted:
                data = {
                    "summary": summary,
                    "experience": experience,
                    "education": education,
                    "skills": [s.strip() for s in skills.split(",")] if skills else []
                }
                res = submit_manual_profile(st.session_state.token, data)
                if res.status_code == 200:
                    st.success("Profile saved successfully!")
                else:
                    st.error(f"Failed to save profile: {res.text}")

    with tab3:
        st.subheader("Tailor Resume for a Job")
        jd_text = st.text_area("Paste the Job Description here", height=300, value=st.session_state.jd_text)
        if st.button("Generate Tailored Resume"):
            if not jd_text.strip():
                st.warning("Please paste a job description first.")
            else:
                st.session_state.jd_text = jd_text
                with st.spinner("AI is tailoring your resume..."):
                    res = generate_tailored_resume(st.session_state.token, jd_text)
                    if res.status_code == 200:
                        res_data = res.json()
                        st.session_state.tailored_data = res_data.get("data", res_data)
                        st.session_state.current_version_id = res_data.get("id")
                        st.success("Resume tailored successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error tailoring resume: {res.text}")
                        
        if st.session_state.tailored_data:
            data = st.session_state.tailored_data
            
            st.divider()
            col_a, col_b = st.columns([2, 1])
            with col_a:
                template_choice = st.selectbox("Choose Template", ["modern", "classic"])
            with col_b:
                st.write("") # Spacer
                st.write("") # Spacer
                if st.button("Generate & Download PDF"):
                    with st.spinner("Compiling LaTeX to PDF..."):
                        if not st.session_state.current_version_id:
                            st.error("No valid version selected. Please tailor or refine again.")
                        else:
                            pdf_res = generate_pdf(st.session_state.token, st.session_state.current_version_id, template_choice)
                            if pdf_res.status_code == 200:
                                st.download_button(
                                    label="📄 Download PDF",
                                    data=pdf_res.content,
                                    file_name="tailored_resume.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("LaTeX compilation failed, please try the other template or check your internet connection for the fallback API. " + pdf_res.text)
            
            st.divider()

            # Assuming the AI returns ats_score directly, or calculate mock
            ats_score = data.get("ats_score", 85)
            
            # Color coding
            color = "normal" if ats_score > 75 else ("off" if ats_score > 50 else "inverse")
            st.metric(label="ATS Match Score", value=f"{ats_score}/100", delta=color)
            
            st.subheader("Tailored Summary")
            st.write(data.get("summary", ""))
            
            st.subheader("Updated Experience")
            for exp in data.get("work_experience", []):
                st.markdown(f"**{exp.get('role', 'Role')} at {exp.get('company', 'Company')}**")
                # If bullet points is a list of strings
                bullets = exp.get("bullet_points", [])
                if isinstance(bullets, list):
                    for bullet in bullets:
                        st.markdown(f"- {bullet}")
                else:
                    st.write(bullets)
                    
            st.subheader("Prioritized Skills")
            skills = data.get("skills", [])
            if isinstance(skills, list):
                st.write(", ".join(skills))
            else:
                st.write(skills)
            
            st.subheader("Keyword Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Matched Keywords**")
                matched = data.get("matched_keywords", [])
                if isinstance(matched, list):
                    st.write(", ".join(matched))
                else:
                    st.write(matched)
            with col2:
                st.write("**Missing Keywords**")
                missing = data.get("missing_keywords", [])
                if isinstance(missing, list):
                    st.write(", ".join(missing))
                else:
                    st.write(missing)
                                
            st.divider()
            st.subheader("Chat to Refine")
            st.write("Want to make changes? Ask the AI to refine this version.")
            feedback = st.text_area("E.g., 'Shorten the summary to 2 lines' or 'Add more metrics to the first job'")
            if st.button("Refine Resume"):
                if feedback.strip():
                    with st.spinner("AI is refining your resume..."):
                        ref_res = refine_resume_api(
                            st.session_state.token, 
                            st.session_state.tailored_data, 
                            feedback, 
                            st.session_state.jd_text
                        )
                        if ref_res.status_code == 200:
                            ref_data = ref_res.json()
                            st.session_state.tailored_data = ref_data.get("data", ref_data)
                            st.session_state.current_version_id = ref_data.get("id")
                            st.success("Resume refined successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error refining resume: {ref_res.text}")
                else:
                    st.warning("Please enter some feedback.")
