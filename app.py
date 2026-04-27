import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# Load model
model = joblib.load("crowd_model.pkl")
columns = joblib.load("model_columns.pkl")

st.title("🏞️ Tourist Crowd Prediction System (TourPulse)")

# -----------------------------
# USER INPUT
# -----------------------------

location = st.selectbox("Select Location", [
    "Kedarnath", "Badrinath", "Rishikesh", "Haridwar",
    "Kashi Vishwanath", "Tirupati", "Vaishno Devi",
    "Taj Mahal", "Jaipur Palace", "Gateway of India"
])

date = st.date_input("Select Date")
time = st.slider("Hour", 0, 23)

weather = st.selectbox("Weather", ["Clear", "Cloudy", "Rain"])

# -----------------------------
# FEATURE ENGINEERING (same as training)
# -----------------------------

dt = datetime.combine(date, datetime.min.time()).replace(hour=time)

hour = dt.hour
day_of_week = dt.weekday()
month = dt.month

is_weekend = 1 if day_of_week >= 5 else 0
is_rush_hour = 1 if 8 <= hour <= 12 else 0

# Simple logic (same as before)
is_holiday = 1 if date.strftime("%Y-%m-%d") in [
    "2025-08-15", "2025-01-26"
] else 0

is_festival = 0
is_long_weekend = is_weekend

is_closed = 1 if location in ["Kedarnath","Badrinath"] and month in [11,12,1,2,3,4] else 0

# Location weight
location_weight = {
    "Kedarnath": 3, "Badrinath": 3,
    "Tirupati": 4, "Vaishno Devi": 4,
    "Kashi Vishwanath": 3,
    "Rishikesh": 2, "Haridwar": 2,
    "Taj Mahal": 3, "Jaipur Palace": 2,
    "Gateway of India": 2
}

weight = location_weight[location]

is_peak_season = 1 if month in [5,6,10,11] else 0

# -----------------------------
# CREATE INPUT DATAFRAME
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

# Add weather columns
for w in ["weather_Cloudy", "weather_Rain"]:
    input_data[w] = 0

if weather == "Cloudy":
    input_data["weather_Cloudy"] = 1
elif weather == "Rain":
    input_data["weather_Rain"] = 1

# Convert to DataFrame
input_df = pd.DataFrame([input_data])

# Match training columns
for col in columns:
    if col not in input_df:
        input_df[col] = 0

input_df = input_df[columns]

# -----------------------------
# PREDICTION
# -----------------------------

if st.button("Predict Crowd"):
    prediction = model.predict(input_df)[0]

    st.subheader(f"Predicted Crowd Level: {prediction}")

    # Smart message (Gemini-style)
    if prediction == "High":
        st.error("⚠️ Heavy crowd expected. Plan your visit carefully.")
    elif prediction == "Medium":
        st.warning("Moderate crowd expected.")
    else:
        st.success("Low crowd. Good time to visit!")
