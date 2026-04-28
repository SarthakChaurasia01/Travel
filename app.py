import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="TourPulse AI",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="collapsed" # Focus on the main dashboard
)

# -----------------------------
# LOAD MODEL (Dummy placeholders commented out for safety)
# -----------------------------
try:
    model = joblib.load("crowd_model.pkl")
    columns = joblib.load("model_columns.pkl")
except FileNotFoundError:
    st.error("⚠️ Model files not found. Please ensure 'crowd_model.pkl' and 'model_columns.pkl' are in the directory.")
    st.stop()

# -----------------------------
# EXTRAORDINARY CSS (Glassmorphism & Gradients)
# -----------------------------
st.markdown("""
<style>
/* Main Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #ffffff;
}

/* Hide Streamlit Header */
[data-testid="stHeader"] {
    background-color: transparent;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
}

/* Gradient Text */
.gradient-text {
    background: -webkit-linear-gradient(45deg, #00C9FF 0%, #92FE9D 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3em;
    margin-bottom: 0px;
}

/* Subtext */
.subtext {
    color: #a0aec0;
    font-size: 1.2em;
    margin-bottom: 30px;
}

/* Custom Button */
.stButton>button {
    background: linear-gradient(45deg, #4f46e5, #ec4899);
    color: white;
    border: none;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-weight: bold;
    font-size: 1.2em;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(45deg, #ec4899, #4f46e5);
    box-shadow: 0 0 15px rgba(236, 72, 153, 0.5);
    color: white;
}

/* Result Cards */
.result-card {
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    animation: fadeIn 1s ease-in-out;
}
.result-high { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
.result-medium { background: linear-gradient(135deg, #f7b733, #fc4a1a); }
.result-low { background: linear-gradient(135deg, #11998e, #38ef7d); }

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HERO SECTION
# -----------------------------
st.markdown("<h1 class='gradient-text'>TourPulse AI 🏞️</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Next-Gen Crowd Intelligence for Tourist & Religious Destinations</p>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# DASHBOARD INPUTS (Moved from sidebar to main for better UI)
# -----------------------------
st.markdown("### 🎛️ Trip Parameters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    location = st.selectbox("📍 Location", [
        "Kedarnath", "Badrinath", "Rishikesh", "Haridwar",
        "Kashi Vishwanath", "Tirupati", "Vaishno Devi",
        "Taj Mahal", "Jaipur Palace", "Gateway of India"
    ])

with col2:
    date = st.date_input("📅 Date")

with col3:
    time_val = st.slider("⏰ Hour (0-23)", 0, 23, 12)

with col4:
    weather = st.selectbox("🌤 Weather", ["Clear", "Cloudy", "Rain"])

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
dt = datetime.combine(date, datetime.min.time()).replace(hour=time_val)

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
    "Kedarnath": 3, "Badrinath": 3, "Tirupati": 4, "Vaishno Devi": 4,
    "Kashi Vishwanath": 3, "Rishikesh": 2, "Haridwar": 2,
    "Taj Mahal": 3, "Jaipur Palace": 2, "Gateway of India": 2
}

weight = location_weight[location]
is_peak_season = int(month in [5,6,10,11])

input_data = {
    "hour": hour, "day_of_week": day_of_week, "month": month,
    "is_weekend": is_weekend, "is_rush_hour": is_rush_hour,
    "is_holiday": is_holiday, "is_festival": is_festival,
    "is_long_weekend": is_long_weekend, "is_closed": is_closed,
    "location_weight": weight, "is_peak_season": is_peak_season,
    "weather_Cloudy": 1 if weather == "Cloudy" else 0,
    "weather_Rain": 1 if weather == "Rain" else 0
}

input_df = pd.DataFrame([input_data])
for col in columns:
    if col not in input_df:
        input_df[col] = 0
input_df = input_df[columns]

# -----------------------------
# SUMMARY METRICS
# -----------------------------
mc1, mc2, mc3 = st.columns(3)
mc1.markdown(f"<div class='glass-card'><h4>📍 Destination</h4><h2 style='color:#00C9FF;'>{location}</h2></div>", unsafe_allow_html=True)
mc2.markdown(f"<div class='glass-card'><h4>📅 Planned Visit</h4><h2 style='color:#92FE9D;'>{date.strftime('%b %d, %Y')} @ {time_val}:00</h2></div>", unsafe_allow_html=True)
mc3.markdown(f"<div class='glass-card'><h4>🌤 Conditions</h4><h2 style='color:#F6D365;'>{weather}</h2></div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# -----------------------------
# PREDICTION ENGINE
# -----------------------------
_, btn_col, _ = st.columns([1, 2, 1]) # Center the button

with btn_col:
    if st.button("🚀 Run Crowd Analytics"):
        
        # Add a slick loading animation
        with st.spinner('Analyzing historical data & weather patterns...'):
            time.sleep(1.5) # Simulate heavy computation for UI effect
            prediction = model.predict(input_df)[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display Result with custom CSS cards
        if prediction == "High":
            st.markdown(f"""
            <div class='result-card result-high'>
                <h1 style='font-size: 3em; margin:0;'>🚨 High Crowd Alert</h1>
                <p style='font-size: 1.2em;'>Expect heavy rush and long waiting queues. Consider rescheduling if possible.</p>
            </div>
            """, unsafe_allow_html=True)
        elif prediction == "Medium":
            st.markdown(f"""
            <div class='result-card result-medium'>
                <h1 style='font-size: 3em; margin:0;'>⚠️ Moderate Crowd</h1>
                <p style='font-size: 1.2em;'>Manageable crowds. A good time to visit, but expect some activity.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='result-card result-low'>
                <h1 style='font-size: 3em; margin:0;'>✨ Low Crowd Expected</h1>
                <p style='font-size: 1.2em;'>Perfect time to visit! Enjoy a peaceful and uncrowded experience.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # -----------------------------
        # AI EXPLANATION & TREND VISUALIZATION
        # -----------------------------
        exp_col, chart_col = st.columns([1, 1.5])
        
        with exp_col:
            st.markdown("### 🧠 AI Insights")
            st.markdown("Here is why the model made this prediction:")
            
            reasons = []
            if is_closed: reasons.append("🚫 Location is currently in closed season")
            if is_weekend: reasons.append("📅 Weekend traffic increases overall visitors")
            if is_peak_season: reasons.append("🏔️ Currently in peak tourist season")
            if is_rush_hour: reasons.append("⏰ You selected peak visiting hours (8 AM - 12 PM)")
            if weather == "Rain": reasons.append("🌧️ Rainy weather significantly reduces footfall")
            if weather == "Clear": reasons.append("☀️ Clear weather encourages more visitors")

            if len(reasons) > 0:
                for r in reasons:
                    st.success(r)
            else:
                st.info("📊 Standard average daily conditions apply.")

        with chart_col:
            st.markdown("### 📈 Simulated 24-Hour Trend")
            # Create a mock bell-curve dataframe to simulate crowd trend across the day
            hours = np.arange(0, 24)
            base_trend = np.exp(-0.5 * ((hours - 12) / 4) ** 2) * 100 
            
            # Adjust mock trend based on current prediction
            if prediction == "High": multiplier = 1.2
            elif prediction == "Medium": multiplier = 0.8
            else: multiplier = 0.4
            
            trend_data = pd.DataFrame({
                "Crowd Volume": base_trend * multiplier
            }, index=hours)
            
            st.area_chart(trend_data, color="#00C9FF")
