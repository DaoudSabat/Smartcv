import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
from template_renderer import TemplateRenderer
import json

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Session
if "cv_file" not in st.session_state:
    st.session_state["cv_file"] = ""

# Page setup
st.set_page_config(page_title="SmartCV", page_icon="💼")
st.title("💼 SmartCV – GPT-based CV Generator")
st.markdown("Generate a professional one-page resume based on your real experience.")

# Template selection
template_options = ["default", "modern", "classic"]
selected_template = st.radio("Choose a CV template:", template_options, horizontal=True)

# User input
st.header("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone")
address = st.text_input("Address")
job_title = st.text_input("Target Job Title")
linkedin = st.text_input("LinkedIn Profile URL (optional)")
st.header("💡 Background Info")
skills = st.text_area("List your technical skills")
experience = st.text_area("Summarize your work experience")
projects = st.text_area("Mention your best projects")
education = st.text_area("Education background")
# Languages section
st.header("🌐 Languages")
language_entries = []
language_count = st.number_input("How many languages do you want to add?", min_value=1, max_value=10, value=1)
for i in range(language_count):
    lang = st.selectbox(f"Language #{i+1}", options=[
        "English", "Arabic", "French", "Spanish", "German", "Hebrew", "Chinese", "Russian", "Hindi", "Other"
    ], key=f"lang_{i}")
    proficiency = st.selectbox(f"Proficiency in {lang}", options=["Basic", "Conversational", "Fluent", "Native"], key=f"prof_{i}")
    language_entries.append(f"{lang} - {proficiency}")

if st.button("🚀 Generate CV"):
    if not name or not email or not job_title or not skills:
        st.warning("Name, email, job title, and skills are required.")
    else:
        with st.spinner("Generating smart CV using AI..."):
            try:
                languages_text = "\n".join(language_entries)
                prompt = f"""
                You are a CV writing assistant. Generate a JSON object with the following structure:
                {{
                "summary": "...",
                "skills": ["...", "..."],
                "education": "...",
                "experience": ["...", "..."],
                "projects": ["...", "..."],
                "languages": ["..."]
                }}
                Make the tone professional and concise, suitable for a one-page CV.
                Use bullet points where applicable.
                👉 Make the content compact and optimized to fit a single A4 page PDF. Limit each section to the most relevant 4–6 items. Avoid repetition, and use short, impactful phrases.
                Candidate Info:
                Name: {name}
                Email: {email}
                Phone: {phone}
                Address: {address}
                LinkedIn: {linkedin}
                Job Title: {job_title}
                Skills: {skills}
                Experience: {experience}
                Projects: {projects}
                Education: {education}
                Languages: {languages_text}
                Return ONLY the JSON object.
                """

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )

                json_output = response.choices[0].message.content.strip()
                generated = json.loads(json_output)

                # Convert list fields to <ul><li> HTML
                def to_bullets(items):
                    if isinstance(items, list):
                        return "<ul>" + "".join([f"<li>{item}</li>" for item in items]) + "</ul>"
                    return items
                
                experience_html = """
                <p><strong>AI Training Freelancer at Outlier</strong><br>
                Remote | 12/2024 – 01/2025<br>
                Evaluated AI-generated code, developed test cases, and optimized performance</p>
                """

                sections = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "linkedin": linkedin,
                    "job_title": job_title,
                    "summary": generated.get("summary", ""),
                    "skills": to_bullets(generated.get("skills", [])),
                    "education": generated.get("education", ""),
                    "experience": to_bullets(generated.get("experience", [])),
                    "projects": to_bullets(generated.get("projects", [])),
                    "languages": to_bullets(generated.get("languages", language_entries)),
                }

                renderer = TemplateRenderer(selected_template)
                pdf_path = renderer.render_cv(sections)
                st.session_state["cv_file"] = pdf_path
                st.success("✅ CV Generated Successfully!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

if st.session_state["cv_file"]:
    with open(st.session_state["cv_file"], "rb") as f:
        st.download_button("⬇️ Download CV PDF", f, file_name="SmartCV.pdf", mime="application/pdf")
