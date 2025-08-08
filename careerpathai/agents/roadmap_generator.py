import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment.")
genai.configure(api_key=api_key)

# Load model
model = genai.GenerativeModel("models/gemini-1.5-flash")


# ✅ This function MUST be at top-level
def generate_roadmap(career_interest: str, skills: str) -> str:
    prompt = f"Generate a step-by-step career roadmap to become a {career_interest}, assuming the user already knows {skills}."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating roadmap: {e}"
