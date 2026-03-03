import streamlit as st
import numpy as np
import joblib
import time

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="FitPulse Pro",
    layout="wide",
    page_icon="im/logo.png"
)

# ==========================================================
# UTILITIES
# ==========================================================
def load_css(file_name: str):
    """Load external CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found.")

@st.cache_resource
def load_model():
    """Load trained ML model."""
    try:
        return joblib.load("fitness_model.pkl")
    except FileNotFoundError:
        return None

def calculate_metrics(height, weight, daily_steps, resting_hr, sleep_hours, water_liters):
    """Compute derived health metrics."""
    bmi = weight / ((height / 100) ** 2)
    activity_intensity = daily_steps / (resting_hr + 1)
    health_index = (sleep_hours * water_liters) / (bmi + 1)
    score = int(min(100,max(30,(health_index * 35) +(activity_intensity / 15))))
    return bmi, activity_intensity, health_index, score

def get_status(prediction):
    """Return status message and recommendations."""
    if prediction == 0:
        return (
            "Needs Improvement",
            "Your recovery and activity balance needs work.",
            [
                "Increase daily steps to 7,000+",
                "Sleep at least 7 hours",
                "Improve hydration consistency",
                "Add 2–3 workout sessions weekly"
            ],
            "https://images.unsplash.com/photo-1599058917212-d750089bc07e?q=80&w=500",
            "Transformation Phase"
        )

    elif prediction == 1:
        return (
            "Average Fitness",
            "You have a solid base. Optimization will elevate you.",
            [
                "Add 1 strength-focused workout",
                "Improve sleep quality",
                "Increase hydration to 3L daily",
                "Maintain consistent cardio"
            ],
            "https://images.unsplash.com/photo-1517964603305-11c0f6f66012?q=80&w=500",
            "Building Strength"
        )

    else:
        return (
            "Peak Performance",
            "Excellent metabolic efficiency detected.",
            [
                "Maintain current routine",
                "Track progressive overload",
                "Prioritize recovery days",
                "Monitor resting heart rate trends"
            ],
            "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=500",
            "Elite Mode"
        )

# ==========================================================
# INITIAL LOAD
# ==========================================================
load_css("style.css")
model = load_model()

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.image("im/logo.png", width=100)
    st.title("FitPulse Pro")
    st.markdown("---")
    st.write("AI-Driven Health Intelligence")
    st.info(
        "AI-powered system that analyzes biometric and lifestyle "
        "inputs to classify overall fitness performance "
        "using intelligent predictive modeling."
    )
    st.write("Tip: Hydrate immediately after waking to boost metabolism.")

# ==========================================================
# HERO SECTION
# ==========================================================
st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)
st.image("im/b1.png", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.title("Fitness Intelligence Dashboard")
st.write("Input your metrics to generate a full metabolic performance profile.")

# ==========================================================
# INPUT SECTION
# ==========================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Biometric Data")
    age = st.number_input("Age", 18, 100, 30)
    height = st.slider("Height (cm)", 120, 220, 170)
    weight = st.slider("Weight (kg)", 30, 150, 70)

with col2:
    st.subheader("Lifestyle Activity")
    daily_steps = st.slider("Daily Steps", 0, 20000, 8000, 500)
    workout_days = st.slider("Workouts / Week", 0, 7, 3)
    sleep_hours = st.slider("Sleep (hrs)", 4.0, 12.0, 7.5)
    water_liters = st.slider("Water (L)", 0.0, 6.0, 2.5)
    resting_hr = st.slider("Resting Heart Rate", 40, 120, 65)

# ==========================================================
# CALCULATE BASE METRICS
# ==========================================================
bmi, activity_intensity, health_index, score = calculate_metrics(
    height, weight, daily_steps, resting_hr, sleep_hours, water_liters
)

st.metric(
    "Calculated BMI",
    f"{bmi:.1f}",
    delta="Healthy" if 18.5 <= bmi <= 25 else "Outside Range"
)

st.divider()

# ==========================================================
# ANALYSIS BUTTON
# ==========================================================
if st.button("Start AI Analysis"):

    if model is None:
        st.error("Model file missing.")
    else:
        with st.spinner("Analyzing metabolic markers..."):
            time.sleep(1.5)

            input_data = np.array([[age, height, weight, bmi,
                                    daily_steps, workout_days,
                                    sleep_hours, water_liters,
                                    resting_hr, activity_intensity,
                                    health_index]])

            prediction = model.predict(input_data)[0]

        status_title, status_text, recommendations, image_url, caption = get_status(prediction)

        # ==================================================
        # RESULTS LAYOUT
        # ==================================================
        res_col1, res_col2 = st.columns([1.5, 1])

        with res_col1:

            if prediction == 0:
                st.error(status_title)
            elif prediction == 1:
                st.warning(status_title)
            else:
                st.success(status_title)

            st.write(status_text)

            # ==============================
            # AI INSIGHTS (ONLY NEW FEATURE)
            # ==============================
            st.markdown("AI Insights")

            insights = []

            if sleep_hours < 6:
                insights.append("⚠ Low sleep detected — recovery efficiency may drop.")

            if water_liters < 2:
                insights.append("Hydration is below optimal range. Aim for 2–3 liters daily.")

            if resting_hr > 75:
                insights.append("Resting heart rate is elevated-cardio conditioning recommended.")

            if not insights:
                st.success("All key recovery markers look balanced. Keep it up!")

            for i in insights:
                st.info(i)

            # ==============================
            # PERFORMANCE SCORE
            # ==============================
            st.markdown("### Performance Score")
            st.progress(score / 100)
            st.metric("Overall Fitness Score", f"{score}/100")

            # ==============================
            # HEALTH INDICATORS
            # ==============================
            st.markdown("### Health Indicators")
            c1, c2, c3 = st.columns(3)
            c1.metric("BMI", f"{bmi:.1f}")
            c2.metric("Activity Intensity", f"{activity_intensity:.1f}")
            c3.metric("Recovery Index", f"{health_index:.2f}")

            # ==============================
            # RECOMMENDATIONS
            # ==============================
            st.markdown("### Personalized Recommendations")
            for tip in recommendations:
                st.write(f"• {tip}")

        with res_col2:
            st.image(image_url, caption=caption)