import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ---------------- Session Initialization ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "detections" not in st.session_state:
    st.session_state.detections = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_image" not in st.session_state:
    st.session_state.last_image = None

# ---------------- Dummy User Data ----------------
USERS = {"admin": "admin123", "user": "pass123"}

# ---------------- Login/Register Screen ----------------
def login_screen():
    st.title("🔐 Smart Waste Management Login")

    choice = st.radio("Login or Register", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if choice == "Login":
            if USERS.get(username) == password:
                st.success("✅ Logged in successfully!")
                st.session_state.logged_in = True
            else:
                st.error("❌ Invalid credentials.")
        elif choice == "Register":
            if username in USERS:
                st.warning("⚠️ Username already exists.")
            else:
                USERS[username] = password
                st.success("🎉 Registered! Please log in.")

# ---------------- Main Waste Classifier App ----------------
def main_app():
    st.title("♻️ Smart Waste Classifier")
    st.markdown("Upload a waste image and input the location to classify and map.")

    uploaded_file = st.file_uploader("📤 Upload Waste Image", type=["jpg", "png", "jpeg"])

    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", format="%.6f")
    with col2:
        lon = st.number_input("Longitude", format="%.6f")

    if st.button("Classify") and uploaded_file:
        try:
            files = {"file": uploaded_file.getvalue()}
            response = requests.post("http://localhost:8000/predict/", files=files)

            if response.status_code == 200:
                result = response.json()
                pred_class = result['class']
                confidence = result['confidence']

                # Store result in session
                st.session_state.last_result = {
                    "class": pred_class,
                    "confidence": confidence,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon
                }
                st.session_state.last_image = uploaded_file.getvalue()

                st.session_state.detections.append(st.session_state.last_result)

            else:
                st.error("❌ Backend prediction failed. Check FastAPI.")
        except Exception as e:
            st.error(f"🚨 Error: {e}")

    # ---------------- Show Persistent Prediction ----------------
    if st.session_state.last_result:
        res = st.session_state.last_result
        st.success(f"🧠 Predicted: **{res['class'].upper()}** with {res['confidence']:.2f}% confidence")
        st.caption(f"📍 Location: ({res['latitude']}, {res['longitude']}) at {res['time']}")
        if st.session_state.last_image:
            st.image(Image.open(BytesIO(st.session_state.last_image)), caption="🖼️ Uploaded Image", use_column_width=True)

    # ---------------- Waste Map ----------------
    if st.session_state.detections:
        st.subheader("🗺️ Waste Detection Map")
        # Use the most recent detection to center the map
        latest_detection = st.session_state.detections[-1]
        map_obj = folium.Map(location=[latest_detection['latitude'], latest_detection['longitude']], zoom_start=13)


        for det in st.session_state.detections:
            popup_text = f"{det['class'].title()} ({det['confidence']:.2f}%)<br>{det['time']}"
            folium.Marker(
                location=[det['latitude'], det['longitude']],
                popup=popup_text,
                icon=folium.Icon(color="green", icon="trash", prefix="fa")
            ).add_to(map_obj)

        st_folium(map_obj, width=700, height=500)

# ---------------- Streamlit Control Flow ----------------
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()

