import streamlit as st
import pydicom
import numpy as np
import tensorflow as tf
from PIL import Image
import os

# === Load the model ===
MODEL_PATH = r"D:\medical_diagnosis\alzheimers_prediction\alzheimers_cnn_model.h5"
if not os.path.exists(MODEL_PATH):
    st.error(f"❌ Model file not found at:\n{MODEL_PATH}\n\nPlease ensure the file exists.")
    st.stop()

model = tf.keras.models.load_model(MODEL_PATH)

# === Label encoder mapping ===
label_map = {
    0: "Alzheimer's Disease (AD)",
    1: "Mild Cognitive Impairment (MCI)",
    2: "Normal Control (NC)"
}

# === Preprocessing function ===
def preprocess_image(file):
    ext = file.name.lower().split('.')[-1]

    if ext == 'dcm':
        dicom = pydicom.dcmread(file)
        pixel_array = dicom.pixel_array
        normalized = (pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))
        image = (normalized * 255).astype(np.uint8)
        image_resized = Image.fromarray(image).resize((128, 128)).convert("L")
    elif ext in ['jpg', 'jpeg', 'png']:
        image = Image.open(file).convert("L")
        image_resized = image.resize((128, 128))
    else:
        raise ValueError("Unsupported file format.")

    image_array = np.array(image_resized).reshape(1, 128, 128, 1) / 255.0
    return image_resized, image_array

# === Streamlit UI ===
st.set_page_config(page_title="Alzheimer's MRI Classifier", layout="centered")
st.title("🧠 Alzheimer's Disease Detection from MRI")
st.markdown("Upload a **DICOM (.dcm)** or **JPG/PNG** MRI image to predict the disease stage.")

# === File Upload ===
uploaded_file = st.file_uploader("📤 Upload MRI Image", type=["dcm", "jpg", "jpeg", "png"])

if uploaded_file:
    try:
        # Preprocess image
        image_display, processed_image = preprocess_image(uploaded_file)

        # Display image
        st.image(image_display, caption="🖼️ MRI Image Preview", width=300)

        # Predict
        prediction = model.predict(processed_image)
        predicted_class = label_map[np.argmax(prediction)]
        confidence = np.max(prediction) * 100

        # Show results
        st.success(f"🧬 *Prediction:* {predicted_class}")
        st.info(f"🔢 Model confidence: {confidence:.2f}%")

    except Exception as e:
        st.error(f"❌ Error processing the file.\n\n**Details:**\n{e}")
