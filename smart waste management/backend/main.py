from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import io

# FastAPI app
app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = load_model("model/waste_classifier.h5")

# Load class names
with open("model/class_names.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

# Image preprocessing
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((128, 128))
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

# API route
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    img = preprocess_image(image_bytes)
    preds = model.predict(img)[0]
    pred_index = int(np.argmax(preds))
    confidence = float(preds[pred_index])

    return {
        "class": class_names[pred_index],
        "confidence": round(confidence * 100, 2)
    }
