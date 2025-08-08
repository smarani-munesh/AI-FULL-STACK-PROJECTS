import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os

# --- Appliance Wattages ---
APPLIANCE_WATTS = {
    "Light": 10,
    "Fan": 70,
    "TV": 120,
    "AC": 1000,
    "Washing Machine": 500,
    "Geyser": 1500,
    "Fridge": 180,
}

USER_FILE = "users.csv"
LOG_FILE = "energy_log.csv"

# --- Initialize files ---
def init_files():
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=["username", "datetime", "block", "floor", "room", "appliance", "status", "people", "energy", "saved", "cost"]).to_csv(LOG_FILE, index=False)

# --- Register Page ---
def register():
    st.title("🔐 Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Register"):
        df = pd.read_csv(USER_FILE)
        if username in df["username"].values:
            st.warning("Username already exists.")
        else:
            df.loc[len(df.index)] = [username, password]
            df.to_csv(USER_FILE, index=False)
            st.success("Registered successfully. Please login.")
            time.sleep(1)
            st.session_state.page = "Login"

# --- Login Page ---
def login():
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        df = pd.read_csv(USER_FILE)
        user_match = df[(df["username"] == username) & (df["password"] == password)]
        if not user_match.empty:
            st.session_state.user = username
            st.session_state.page = "Dashboard"
        else:
            st.error("Invalid credentials.")

# --- Dashboard Page ---
def dashboard():
    st.title("📊 Energy Management Dashboard")
    st.markdown("#### 📍 Select Location")
    block = st.selectbox("Block", ["A", "B", "C"])
    floor = st.selectbox("Floor", ["1", "2", "3"])
    room = st.selectbox("Room", ["101", "102", "103"])
    people = st.slider("Number of People in Room", 0, 10, 1)

    st.markdown("#### 💡 Appliance Controls")
    energy_used, energy_saved, cost = 0, 0, 0
    logs = []

    for appliance, watts in APPLIANCE_WATTS.items():
        status = st.checkbox(f"{appliance}", value=True)
        energy = (watts / 1000) * 1  # 1 hour
        appliance_cost = energy * 8  # ₹8 per kWh

        if status:
            energy_used += energy
            cost += appliance_cost
            saved = 0
        else:
            energy_saved += energy
            saved = energy

        logs.append({
            "username": st.session_state.user,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "block": block,
            "floor": floor,
            "room": room,
            "appliance": appliance,
            "status": "ON" if status else "OFF",
            "people": people,
            "energy": energy if status else 0,
            "saved": saved,
            "cost": appliance_cost if status else 0
        })

    st.write("")
    st.metric("⚡ Energy Consumed (kWh)", round(energy_used, 2))
    st.metric("💸 Cost Estimate (₹)", round(cost, 2))
    st.metric("🌱 Energy Saved (kWh)", round(energy_saved, 2))

    st.markdown("#### 🧠 Smart Suggestions")
    if people == 0:
        st.info("No people in the room. Consider turning off all appliances.")
    if energy_saved > 0:
        st.success(f"Good job! You saved {round(energy_saved, 2)} kWh.")

    # Save log
    df_log = pd.read_csv(LOG_FILE)
    df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)
    df_log.to_csv(LOG_FILE, index=False)

    st.download_button("📥 Download My Energy Report", df_log[df_log["username"] == st.session_state.user].to_csv(index=False), file_name="energy_report.csv")

# --- Main Controller ---
def main():
    st.set_page_config(page_title="Residential Energy Saver", layout="centered")
    init_files()

    if "page" not in st.session_state:
        st.session_state.page = "Login"

    if st.session_state.page == "Login":
        login()
        st.markdown("---")
        if st.button("Go to Register"):
            st.session_state.page = "Register"

    elif st.session_state.page == "Register":
        register()
        st.markdown("---")
        if st.button("Back to Login"):
            st.session_state.page = "Login"

    elif st.session_state.page == "Dashboard":
        dashboard()

main()
