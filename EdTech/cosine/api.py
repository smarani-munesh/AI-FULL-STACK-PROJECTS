# edtech_backend.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import random
import torch
from transformers import pipeline

app = FastAPI()

# === Load Dataset (Optional: Replace with DB) ===
data_path = "edtech_adaptive_learning_dataset.csv"
df = pd.read_csv(data_path)

# === Load Sentiment Analysis Model ===
sentiment_analyzer = pipeline("sentiment-analysis")

# === Pydantic Models ===
class UserLearningData(BaseModel):
    user_id: int
    topic: str
    time_spent: int
    quiz_score: int
    preference: str
    feedback: str
    rating: int

class FeedbackText(BaseModel):
    feedback: str

# === Route: Submit User Learning Data ===
@app.post("/submit_data")
def submit_learning_data(data: UserLearningData):
    global df
    new_data = pd.DataFrame([data.dict()])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(data_path, index=False)
    return {"message": "Data submitted successfully."}

# === Route: Get Recommendations ===
@app.get("/get_recommendations/{user_id}")
def get_recommendations(user_id: int):
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        return {"message": "User not found."}
    
    # Simple logic: Recommend topics not yet seen
    seen_topics = user_data['topic'].unique().tolist()
    all_topics = df['topic'].unique().tolist()
    unseen_topics = list(set(all_topics) - set(seen_topics))
    if not unseen_topics:
        unseen_topics = all_topics

    recommendations = random.sample(unseen_topics, k=min(3, len(unseen_topics)))
    return {"recommended_topics": recommendations}

# === Route: Analyze Feedback Sentiment ===
@app.post("/analyze_feedback")
def analyze_feedback(feedback: FeedbackText):
    result = sentiment_analyzer(feedback.feedback)
    return {"feedback_sentiment": result[0]}

# === Route: Adaptive Assessment Generator ===
@app.get("/adaptive_assessment/{user_id}")
def adaptive_assessment(user_id: int):
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        return {"message": "User not found."}

    avg_score = user_data['quiz_score'].mean()

    # Simulate difficulty level based on avg score
    if avg_score >= 80:
        difficulty = "Advanced"
    elif avg_score >= 50:
        difficulty = "Intermediate"
    else:
        difficulty = "Beginner"

    # Simulate assessment
    sample_questions = {
        "Beginner": ["What is 2 + 2?", "Define variable."],
        "Intermediate": ["Solve x: 2x + 5 = 15", "Explain slope in linear equations."],
        "Advanced": ["Differentiate f(x) = x^2 + 3x", "What is an eigenvector?"]
    }

    questions = sample_questions[difficulty]
    return {
        "assessment_level": difficulty,
        "questions": questions
    }

# === Route: Chatbot (LLM Tutor Placeholder) ===
@app.post("/chatbot")
async def chatbot(request: Request):
    data = await request.json()
    user_query = data.get("query")
    # You can plug in Hugging Face Transformers here later
    return {"reply": f"You asked: '{user_query}'. This is a placeholder reply."}
