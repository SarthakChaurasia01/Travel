import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="TourPulse",
    page_icon="🏞️",
    layout="wide"
)

# -----------------------------
# LOAD MODEL
# -----------------------------
model = joblib.load("crowd_model.pkl")
columns = joblib.load("model_columns.pkl")

# -----------------------------
# CUSTOM CSS (UI MAGIC 🔥)
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #0f172a;
}
h1, h2, h3, h4 {
    color: #ffffff;
}
.stButton>button {
    background-color: #4f46e5;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.metric-box {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🏞️ TourPulse AI")
st.markdown("### Smart Crowd Prediction for Tourist & Religious Places")

st.markdown("---")

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("🧾 Input Parameters")

location = st.sidebar.selectbox("📍 Location", [
    "Kedarnath", "Badrinath", "Rishikesh", "Haridwar",
    "Kashi Vishwanath", "Tirupati", "Vaishno Devi",
    "Taj Mahal", "Jaipur Palace", "Gateway of India"
])

date = st.sidebar.date_input("📅 Select Date")
time = st.sidebar.slider("⏰ Hour", 0, 23)

weather = st.sidebar.selectbox("🌤 Weather", ["Clear", "Cloudy", "Rain"])

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
dt = datetime.combine(date, datetime.min.time()).replace(hour=time)

hour = dt.hour
day_of_week = dt.weekday()
month = dt.month

is_weekend = int(day_of_week >= 5)
is_rush_hour = int(8 <= hour <= 12)

is_holiday = int(date.strftime("%Y-%m-%d") in ["2025-08-15", "2025-01-26"])
is_festival = 0
is_long_weekend = is_weekend

is_closed = int(location in ["Kedarnath","Badrinath"] and month in [11,12,1,2,3,4])

location_weight = {
    "Kedarnath": 3, "Badrinath": 3,
    "Tirupati": 4, "Vaishno Devi": 4,
    "Kashi Vishwanath": 3,
    "Rishikesh": 2, "Haridwar": 2,
    "Taj Mahal": 3, "Jaipur Palace": 2,
    "Gateway of India": 2
}

weight = location_weight[location]
is_peak_season = int(month in [5,6,10,11])

# -----------------------------
# INPUT DATA
# -----------------------------
input_data = {
    "hour": hour,
    "day_of_week": day_of_week,
    "month": month,
    "is_weekend": is_weekend,
    "is_rush_hour": is_rush_hour,
    "is_holiday": is_holiday,
    "is_festival": is_festival,
    "is_long_weekend": is_long_weekend,
    "is_closed": is_closed,
    "location_weight": weight,
    "is_peak_season": is_peak_season,
}

for w in ["weather_Cloudy", "weather_Rain"]:
    input_data[w] = 0

if weather == "Cloudy":
    input_data["weather_Cloudy"] = 1
elif weather == "Rain":
    input_data["weather_Rain"] = 1

input_df = pd.DataFrame([input_data])

for col in columns:
    if col not in input_df:
        input_df[col] = 0

input_df = input_df[columns]

# -----------------------------
# MAIN DISPLAY
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='metric-box'><h4>📍 Location</h4><h2>{location}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-box'><h4>📅 Date</h4><h2>{date}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-box'><h4>🌤 Weather</h4><h2>{weather}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# PREDICTION BUTTON
# -----------------------------
if st.button("🚀 Predict Crowd Level"):

    prediction = model.predict(input_df)[0]

    st.subheader("📊 Prediction Result")

    if prediction == "High":
        st.error("🔴 High Crowd Expected")
        st.markdown("⚠️ Expect heavy rush due to peak conditions. Plan carefully.")

    elif prediction == "Medium":
        st.warning("🟡 Moderate Crowd Expected")
        st.markdown("👍 Manageable crowd. Visit during non-peak hours.")

    else:
        st.success("🟢 Low Crowd Expected")
        st.markdown("✨ Great time to visit with minimal crowd.")

    st.markdown("---")

    # SMART AI EXPLANATION
    st.subheader("🧠 Why this prediction?")

    reasons = []

    if is_weekend:
        reasons.append("Weekend traffic increases visitors")
    if is_peak_season:
        reasons.append("Peak tourist season")
    if is_rush_hour:
        reasons.append("Peak visiting hours")
    if weather == "Rain":
        reasons.append("Rain reduces crowd")

    if len(reasons) > 0:
        for r in reasons:
            st.write("•", r)
    else:
        st.write("Normal conditions")
