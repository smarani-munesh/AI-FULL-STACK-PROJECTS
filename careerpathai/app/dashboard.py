import streamlit as st
import sys
import os

# Add parent directory to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import custom agents
from agents.job_scraper import scrape_jobs
from agents.skill_matcher import match_skills
from agents.roadmap_generator import generate_roadmap

# Dummy certification mapping
cert_map = {
    "python": ["Coursera: Python for Everybody", "edX: Intro to Python"],
    "machine learning": ["Google ML Crash Course", "Coursera: ML by Andrew Ng"],
    "data analytics": ["Kaggle Data Cleaning", "IBM Data Analyst (Coursera)"],
    "deep learning": ["FastAI Practical DL", "DeepLearning.AI Specialization"],
    "flutter": ["AppBrewery Flutter Course", "Google Flutter Bootcamp (Udemy)"],
    "web development": ["CS50 Web Dev", "Frontend Masters HTML/CSS"]
}

# Set Streamlit page config
st.set_page_config(page_title="SkillBridge AI", layout="centered")
st.title("🎯 SkillBridge AI - Career Roadmap Generator")

# User Inputs
st.subheader("📥 Enter Your Profile")
skills = st.text_area("🔧 Skills (comma-separated)", "python, machine learning, deep learning")
interests = st.text_input("🎯 Career Interest (e.g., Data Scientist, AI Engineer)", "data scientist")

# Submit button
if st.button("🚀 Generate My Career Plan"):
    with st.spinner("🧠 Thinking..."):

        # --- JOB SCRAPING ---
        st.subheader("📝 Matching Job Roles")
        query = interests.lower().strip().replace(" ", "-")  # URL-safe
        job_results = scrape_jobs(query)

        if job_results and "Error" not in job_results[0]:
            matched_jobs = match_skills(skills, job_results)
            if matched_jobs:
                for job in matched_jobs[:5]:
                    st.markdown(f"✅ {job}")
            else:
                st.warning("No job roles matched your skills.")
        else:
            st.error("❌ Job scraping failed. Try a different query or check internet connection.")

        # --- CERTIFICATIONS ---
        st.subheader("📚 Recommended Certifications")
        suggested_certs = []
        for skill in skills.split(","):
            s = skill.strip().lower()
            if s in cert_map:
                suggested_certs.extend(cert_map[s])
        if suggested_certs:
            for cert in set(suggested_certs):
                st.markdown(f"🔗 {cert}")
        else:
            st.info("No matching certifications found for your current skills.")

        # --- ROADMAP GENERATION ---
        st.subheader("🧭 Personalized Learning Roadmap")
        try:
            roadmap = generate_roadmap(interests, skills)
            st.markdown(roadmap)
        except Exception as e:
            st.error(f"⚠️ Error generating roadmap: {e}")
