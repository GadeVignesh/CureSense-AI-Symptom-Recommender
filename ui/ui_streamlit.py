import streamlit as st
import requests
import speech_recognition as sr
import pandas as pd
import difflib
import io
import os
from datetime import datetime
import plotly.express as px

API_BASE = "https://curesense-ai-symptom-recommender-4.onrender.com"
APP_TITLE = "⚕ CureSense — AI Symptom Recommender"
PRIMARY_COLOR = "#007bff"
BG_COLOR = "#f4f8ff"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#1a1a1a"
SUB_TITLE_COLOR = "#7066AB"
HISTORY_FILE = "data/history.csv"

def save_history_entry(entry: dict):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    try:
        if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
            pd.DataFrame([entry]).to_csv(HISTORY_FILE, index=False)
        else:
            try:
                df = pd.read_csv(HISTORY_FILE)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame(columns=list(entry.keys()))
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        import traceback
        st.error(f"Error saving history: {e}")
        st.text(traceback.format_exc())

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        if os.path.getsize(HISTORY_FILE) == 0:
            return []
        df = pd.read_csv(HISTORY_FILE)
        if not df.empty and len(df.columns) > 0:
            return df.to_dict("records")
        return []
    except pd.errors.EmptyDataError:
        return []
    except Exception as e:
        import traceback
        st.error(f"Error loading history: {e}")
        st.text(traceback.format_exc())
        return []

st.set_page_config(page_title=APP_TITLE, layout="centered", page_icon="⚕")

st.markdown(f"""
    <style>
        html, body, [class*="css"]  {{
            background-color: {BG_COLOR} !important;
            color: {TEXT_COLOR} !important;
        }}
        .main {{
            background-color: {BG_COLOR};
        }}
        .block-container {{
            padding: 2rem 3rem !important;
            max-width: 900px;
            margin: auto;
        }}
        .big-title {{
            font-size: 36px;
            font-weight: 700;
            color: {PRIMARY_COLOR};
            text-align: center;
            margin-bottom: 0.5rem;
        }}
        h4 {{
            text-align: center;
            margin-bottom: 0.5rem;
            color: #333;
        }}
        .login-card {{
            background-color: {CARD_COLOR};
            border-radius: 12px;
            padding: 2rem 2.5rem;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            max-width: 420px;
            margin: 1.5rem auto 1rem auto;
            text-align: center;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 600;
            color: {SUB_TITLE_COLOR};
            margin-top: 1.5rem;
        }}
        div[data-testid="stFormSubmitButton"] > button {{
            display: block;
            margin: 1.5rem auto;
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 0px !important;
            width: 200px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .stButton > button {{
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            border-radius: 6px !important;
            padding: 0.6rem 1rem !important;
            font-weight: 500 !important;
            border: none !important;
        }}
        .stTextInput > div > div > input {{
            border-radius: 6px !important;
            border: 1px solid #ccc !important;
            background-color: white !important;
            color: #000 !important;
        }}
        .stTextArea > div > textarea {{
            border-radius: 6px !important;
            border: 1px solid #ccc !important;
            background-color: white !important;
            color: #000 !important;
        }}
        div[data-testid="stMarkdownContainer"] p:empty {{
            display: none !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlock"] > div:empty {{
            display: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
    </style>
""", unsafe_allow_html=True)

def api_post(path, json_data=None, headers=None):
    url = f"{API_BASE.rstrip('/')}{path}"
    return requests.post(url, json=json_data or {}, headers=headers or {}, timeout=15)

def transcribe_audio(uploaded_file):
    if not uploaded_file:
        return ""
    r = sr.Recognizer()
    try:
        uploaded_file.seek(0)
        bio = io.BytesIO(uploaded_file.read())
        with sr.AudioFile(bio) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except Exception as e:
        st.error(f"Audio transcription failed: {e}")
        return ""

defaults = {
    "token": None,
    "username": None,
    "voice_text": "",
    "history_cache": load_history(),
    "show_register": False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if not st.session_state.token:
    st.markdown(f"<div class='big-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown("<h4>Please log in to continue</h4>", unsafe_allow_html=True)

    if not st.session_state.show_register:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 User Login")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            login_btn = st.form_submit_button("Login", use_container_width=False)
            if login_btn:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    try:
                        r = api_post("/auth/login", {"username": username, "password": password})
                        if r.status_code == 200:
                            st.session_state.token = r.json()["token"]
                            st.session_state.username = username
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Login failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
        if st.button("🆕 New User? Register Here"):
            st.session_state.show_register = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        with st.form("register_form", clear_on_submit=False):
            st.markdown("#### ✳️ Create New Account")
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            register_btn = st.form_submit_button("Register", use_container_width=False)
            if register_btn:
                if not new_user or not new_pass:
                    st.warning("Please fill all fields.")
                else:
                    try:
                        r = api_post("/auth/register", {"username": new_user, "password": new_pass})
                        if r.status_code == 200:
                            st.success("✅ Account created successfully! You can now log in.")
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Login"):
            st.session_state.show_register = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(f"<div class='big-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(f"Welcome, **{st.session_state.username}** 👋", unsafe_allow_html=True)
with header_col2:
    if st.button("🚪 Logout"):
        for k in ["token", "username"]:
            st.session_state[k] = None
        st.rerun()

tab_titles = ["🏠 Home", "💬 Symptom Analyzer", "📜 History", "📊 Dashboard"]
tabs = st.tabs(tab_titles)
tab_home, tab_predict, tab_history, tab_dashboard = tabs

with tab_home:
    st.markdown("## ⚕ Welcome to CureSense!")
    st.markdown("> *Empowering you with AI-driven health insights.*")
    st.markdown("""
    CureSense helps you understand your symptoms 
    and provides AI-powered recommendations for possible causes and medications.
    Our mission is to make early symptom understanding accessible, accurate, and user-friendly.
    """)
    st.markdown("### ⚙️ Key Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🤖 AI Symptom Analyzer")
        st.write("Instantly get possible conditions and treatments based on your symptoms.")
    with col2:
        st.markdown("#### 🗣️ Voice Input Support")
        st.write("Speak or upload an audio file — CureSense automatically detects your symptoms.")
    with col3:
        st.markdown("#### 💊 Smart Recommendations")
        st.write("Receive tailored medication suggestions and alerts when a doctor’s visit is needed.")
    st.markdown("---")
    st.info("💡 Use the **Symptom Analyzer** tab to begin your health analysis journey.")
    st.markdown("---")
    st.markdown("""
    ### ⚠️ Disclaimer
    CureSense is an AI-powered recommendation system designed for informational purposes only.  
    It should not replace professional medical consultation.  
    Always seek the advice of a qualified healthcare provider.
    """)

with tab_predict:
    st.markdown("<div class='section-title'>Symptom Analyzer</div>", unsafe_allow_html=True)
    col_main, col_side = st.columns([3, 1])
    with col_main:
        st.markdown("#### 🩺 Describe Your Symptoms")
        input_mode = st.radio("Input Type", ["Text Entry", "Voice Input"], horizontal=True)
        if input_mode == "Text Entry":
            symptoms = st.text_area("Enter symptoms", value=st.session_state.voice_text, height=100)
        else:
            with st.expander("🎙 Voice Input Options", expanded=True):
                colv1, colv2 = st.columns(2)
                with colv1:
                    if st.button("🎧 Record Live"):
                        try:
                            r = sr.Recognizer()
                            with sr.Microphone() as src:
                                st.info("🎤 Listening... Speak now.")
                                audio = r.listen(src, timeout=10)
                            text = r.recognize_google(audio)
                            st.session_state.voice_text = text
                            st.success(f"Transcribed: {text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                with colv2:
                    uploaded = st.file_uploader("Upload Audio (WAV/MP3)", type=["wav", "mp3"])
                    if uploaded:
                        text = transcribe_audio(uploaded)
                        if text:
                            st.session_state.voice_text = text
                            st.success(f"Transcribed: {text}")
            symptoms = st.text_area("Edit recognized text", value=st.session_state.voice_text, height=100)
        severity = st.slider("Severity (0–10)", 0, 10, 5)
        duration = st.number_input("Duration (days)", 0, 365, 1)
        temp = st.number_input("Body Temperature (°C)", 30.0, 45.0, 36.6, 0.1)
    with col_side:
        st.markdown("#### 🤖 Smart Health Advisory")
        if severity >= 8 or temp >= 39:
            st.error("⚠️ High severity detected — this could be an emergency!")
            st.markdown("""
            - 📞 Call **108** or visit the nearest hospital  
            - 🧊 Stay hydrated and rest in a cool place  
            - 💬 Consult a **General Physician** immediately
            """)
        elif severity >= 5:
            st.warning("🩺 Moderate symptoms — monitor closely and rest well.")
        else:
            st.info("✅ Mild condition — stay hydrated and rest. Monitor your symptoms.")
    st.markdown("<hr style='margin-top:20px;margin-bottom:20px;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    analyze = st.button("🔍 Analyze Symptoms", use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)
    if analyze:
        if not symptoms.strip():
            st.warning("Please enter symptoms first.")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            emergency = False
            is_emergency = emergency or (severity >= 8 or temp >= 39)
            payload = {
                "symptoms": symptoms,
                "severity": severity,
                "duration_days": duration,
                "temperature_c": temp,
                "emergency": is_emergency
            }
            try:
                resp = api_post("/predict", json_data=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    diseases = data.get("predicted_diseases", [])
                    meds = data.get("medications", [])
                    doctor_suggestions = {
                        "fever": "General Physician",
                        "cold": "ENT Specialist",
                        "migraine": "Neurologist",
                        "asthma": "Pulmonologist",
                        "diabetes": "Endocrinologist",
                        "heart disease": "Cardiologist",
                        "skin rash": "Dermatologist",
                        "stomach pain": "Gastroenterologist",
                        "eye infection": "Ophthalmologist",
                        "depression": "Psychiatrist",
                        "covid": "Infectious Disease Specialist"
                    }
                    if diseases:
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.success("✅ Analysis Complete!")
                        st.markdown("### 🦠 Predicted Diseases")
                        for d, c in diseases:
                            st.progress(c / 100)
                            st.write(f"**{d.title()}** — {c}% Confidence")
                        if meds:
                            st.markdown("### 💊 Recommended Medications")
                            st.write(", ".join(meds))
                        st.markdown("### 🧑‍⚕️ Suggested Doctors")
                        for d, _ in diseases:
                            doctor = next((spec for key, spec in doctor_suggestions.items() if key in d.lower()), "General Physician")
                            st.write(f"**{d.title()} → {doctor}**")
                    else:
                        st.info("No diseases detected. Try again with different symptoms.")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry = {
                        "Date & Time": timestamp,
                        "Symptoms": symptoms,
                        "Predicted Diseases": ", ".join([d for d, _ in diseases]),
                        "Medications": ", ".join(meds) if meds else "None",
                        "Suggested Doctors": ", ".join([next((spec for key, spec in doctor_suggestions.items() if key in d.lower()), "General Physician") for d, _ in diseases])
                    }
                    st.session_state.history_cache.append(entry)
                    save_history_entry(entry)
                    st.success("📜 Prediction saved to history successfully!")
                else:
                    st.error(f"Server Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

with tab_history:
    st.markdown("<div class='section-title'>Prediction History</div>", unsafe_allow_html=True)
    if not st.session_state.history_cache:
        st.info("No predictions yet.")
    else:
        df = pd.DataFrame(st.session_state.history_cache)
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab_dashboard:
    st.markdown("<div class='section-title'>Medical Analysis Dashboard</div>", unsafe_allow_html=True)
    if not st.session_state.history_cache:
        st.info("No data available yet.")
    else:
        df = pd.DataFrame(st.session_state.history_cache).fillna("Unknown")
        total_predictions = len(df)
        disease_str = ",".join(df.get("Predicted Diseases", "Unknown").astype(str))
        disease_list = [d.strip() for d in disease_str.split(",") if d.strip() and d.lower() != "none"]
        unique_diseases = len(set(disease_list))
        doc_str = ",".join(df.get("Suggested Doctors", "Unknown").astype(str))
        doc_list = [d.strip() for d in doc_str.split(",") if d.strip() and d.lower() != "none"]
        med_str = ",".join(df.get("Medications", "Unknown").astype(str))
        med_list = [m.strip() for m in med_str.split(",") if m.strip() and m.lower() != "none"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🧾 Total Predictions", total_predictions)
        col2.metric("🧬 Unique Diseases", unique_diseases)
        col3.metric("💊 Unique Medications", len(set(med_list)))
        col4.metric("🏥 Unique Doctors", len(set(doc_list)))
        if disease_list:
            disease_counts = pd.Series(disease_list).value_counts().reset_index()
            disease_counts.columns = ["Disease", "Count"]
            most_common_disease = disease_counts.iloc[0]["Disease"]
        else:
            disease_counts = pd.DataFrame(columns=["Disease", "Count"])
            most_common_disease = "No data"
        if doc_list:
            doctor_counts = pd.Series(doc_list).value_counts().reset_index()
            doctor_counts.columns = ["Doctor", "Count"]
            most_common_doctor = doctor_counts.iloc[0]["Doctor"]
        else:
            doctor_counts = pd.DataFrame(columns=["Doctor", "Count"])
            most_common_doctor = "No data"
        st.markdown(f"### 🦠 Most Common Disease: **{most_common_disease}**")
        st.markdown(f"### 🧑‍⚕️ Most Suggested Doctor: **{most_common_doctor}**")
        if not disease_counts.empty:
            st.plotly_chart(px.bar(disease_counts, x="Disease", y="Count", title="🧬 Disease Frequency"), use_container_width=True)
        if med_list:
            med_counts = pd.Series(med_list).value_counts().reset_index()
            med_counts.columns = ["Medication", "Count"]
            st.plotly_chart(px.pie(med_counts, values="Count", names="Medication", title="💊 Medication Distribution"), use_container_width=True)
        if not doctor_counts.empty:
            st.plotly_chart(px.bar(doctor_counts, x="Doctor", y="Count", title="🏥 Doctor Recommendation Frequency"), use_container_width=True)

st.markdown(
    """
    <hr style='margin-top:40px; margin-bottom:20px; border: 1px solid #ddd;'>

    <div style="
        text-align:center; 
        padding: 15px; ;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 15px;
        color: #555;
    ">
        ⚕ <b style="color:#007bff;">CureSense</b> — Your AI Symptom-to-Medication Recommender<br>
        <span style="font-size:13px;">Empowering smarter healthcare decisions through AI</span><br>
        <span style="font-size:12px;">© 2025 CureSense | All Rights Reserved</span><br><br>
    </div>
    """,
    unsafe_allow_html=True
)



