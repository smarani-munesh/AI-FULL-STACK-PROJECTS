# edtech_frontend.py

import streamlit as st
import requests
import google.generativeai as genai

API_URL = "http://127.0.0.1:8000"  # Change this if hosted elsewhere

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyAW6glS-RxjUUUwXvq-GUbM_rcBwMxAWJI")
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat(history=[])

st.set_page_config(page_title="EdTech Adaptive Learning Platform", layout="centered")
st.title("📚 EdTech Adaptive Learning Platform")

# === Sidebar ===
menu = st.sidebar.selectbox("Choose a feature", [
    "Submit Learning Data",
    "Get Recommendations",
    "Adaptive Assessment",
    "Feedback Analyzer",
    "Chatbot Tutor"
])

# === 1. Submit Learning Data ===
if menu == "Submit Learning Data":
    st.header("📥 Submit Learning Data")
    with st.form("submit_form"):
        user_id = st.number_input("User ID", min_value=1, value=101)
        topic = st.selectbox("Topic", ["Algebra", "Geometry", "Calculus", "Trigonometry", "Statistics"])
        time_spent = st.slider("Time Spent (minutes)", 5, 120, 30)
        quiz_score = st.slider("Quiz Score", 0, 100, 70)
        preference = st.selectbox("Learning Preference", ["Visual", "Text", "Audio", "Interactive"])
        feedback = st.text_area("Feedback")
        rating = st.slider("Content Rating (1-5)", 1, 5, 4)
        submitted = st.form_submit_button("Submit")

    if submitted:
        payload = {
            "user_id": user_id,
            "topic": topic,
            "time_spent": time_spent,
            "quiz_score": quiz_score,
            "preference": preference,
            "feedback": feedback,
            "rating": rating
        }
        res = requests.post(f"{API_URL}/submit_data", json=payload)
        st.success(res.json().get("message"))

# === 2. Get Recommendations ===
elif menu == "Get Recommendations":
    st.header("📌 Learning Recommendations")
    user_id = st.number_input("Enter your User ID", min_value=1)
    if st.button("Get Recommendations"):
        res = requests.get(f"{API_URL}/get_recommendations/{user_id}")
        if res.status_code == 200:
            data = res.json()
            st.write("### Recommended Topics:")
            st.write(data.get("recommended_topics", []))
        else:
            st.error("User not found.")

# === 3. Adaptive Assessment ===
elif menu == "Adaptive Assessment":
    st.header("📝 Adaptive Assessment")
    user_id = st.number_input("Enter your User ID for assessment", min_value=1)
    if st.button("Generate Assessment"):
        # Get user history
        history_res = requests.get(f"{API_URL}/get_recommendations/{user_id}")
        if history_res.status_code != 200:
            st.error("User not found.")
        else:
            # Generate prompt for LLM
            prompt = f"Generate 3 personalized assessment questions for a student who has an average performance score in topics like {', '.join(history_res.json().get('recommended_topics', []))}. Make them adaptive and helpful."
            try:
                response = chat.send_message(prompt)
                st.write("### Level: AI-Generated")
                st.write("### Questions:")
                for line in response.text.strip().split('\n'):
                    if line.strip():
                        st.write(f"- {line.strip()}")
            except Exception as e:
                st.error(f"Failed to generate questions: {e}")

# === 4. Feedback Analyzer ===
elif menu == "Feedback Analyzer":
    st.header("💬 Feedback Sentiment Analysis")
    feedback = st.text_area("Enter feedback to analyze")
    if st.button("Analyze Sentiment"):
        res = requests.post(f"{API_URL}/analyze_feedback", json={"feedback": feedback})
        if res.status_code == 200:
            sentiment = res.json().get("feedback_sentiment")
            st.write(f"**Label:** {sentiment['label']}, **Score:** {round(sentiment['score'], 2)}")
        else:
            st.error("Analysis failed.")

# === 5. Chatbot Tutor ===
elif menu == "Chatbot Tutor":
    st.header("🤖 AI Tutor Chatbot (Gemini)")
    query = st.text_input("Ask something about your subject")
    if st.button("Ask"):
        try:
            response = chat.send_message(query)
            st.write("### Tutor Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Chatbot error: {e}")
