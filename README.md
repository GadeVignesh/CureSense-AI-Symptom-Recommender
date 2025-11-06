CureSense — AI Symptom-to-Medication Recommender
===========================================================

CureSense is an AI-powered healthcare web application that helps users understand their symptoms, predict possible diseases, recommend medications, and suggest relevant doctors. 
Built using Python, Flask, and Streamlit, CureSense combines artificial intelligence with an intuitive interface to make early disease detection accessible, accurate, and user-friendly.

-----------------------------------------------------------
🌟 FEATURES
-----------------------------------------------------------
• AI Symptom Analyzer – Predicts possible diseases with confidence scores.
• Medication Recommender – Suggests appropriate medications for each disease.
• Doctor Suggestion System – Recommends relevant medical specialists.
• Voice Input Support – Allows users to describe symptoms by speaking.
• Smart Health Advisory – Detects emergencies such as high fever or severe symptoms.
• Secure Authentication – Login and registration for personalized experience.
• Health History Dashboard – Saves previous analyses for easy tracking.
• Interactive Analytics – Displays disease and medication insights visually.

-----------------------------------------------------------
🧠 TECH STACK
-----------------------------------------------------------
Frontend: Streamlit
Backend: Flask (REST API)
Language: Python
Database: CSV (Local Storage)
Libraries: Pandas, Plotly, SpeechRecognition, Flask-CORS, Difflib, Requests

-----------------------------------------------------------
🗂️ PROJECT STRUCTURE
-----------------------------------------------------------
CureSense/
│
├── app/
│   ├── app.py              → Flask backend logic
│   ├── auth.py             → Authentication routes
│   ├── utils.py            → Utility & ML model functions
│   ├── db.py               → Local database handler
│   ├── __init__.py
│
├── ui/
│   ├── ui_streamlit.py     → Streamlit frontend interface
│
├── models/
│   ├── model.pkl           → ML model for disease prediction
│   ├── mlb.pkl             → Label encoder
│
├── data/
│   ├── history.csv         → Stores prediction history
│   ├── symptoms_dataset.csv (optional / add manually)
│
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.txt

-----------------------------------------------------------
⚙️ INSTALLATION & SETUP
-----------------------------------------------------------

1. Clone the Repository:
   git clone https://github.com/your-username/CureSense-AI-Symptom-Recommender.git
   cd CureSense-AI-Symptom-Recommender

2. Create a Virtual Environment:
   Windows:
      python -m venv venv
      venv\Scripts\activate
   Mac/Linux:
      python3 -m venv venv
      source venv/bin/activate

3. Install Dependencies:
   pip install -r requirements.txt

-----------------------------------------------------------
▶️ RUNNING THE APPLICATION
-----------------------------------------------------------

1. Start the Flask Backend:
   cd app
   python app.py

   (Backend runs at: http://127.0.0.1:5000)

2. Start the Streamlit Frontend:
   cd ..
   streamlit run ui/ui_streamlit.py

   (Frontend opens automatically in the browser)

-----------------------------------------------------------
📊 SAMPLE WORKFLOW
-----------------------------------------------------------
1. User enters or speaks symptoms.
2. AI model predicts possible diseases.
3. System recommends suitable medications and doctors.
4. Smart advisory detects emergencies or severe conditions.
5. Results are saved in user’s health history.

-----------------------------------------------------------
🧩 KEY SKILLS USED
-----------------------------------------------------------
1. Python
2. Flask
3. Streamlit
4. Machine Learning
5. Natural Language Processing (NLP)

-----------------------------------------------------------
💬 PROJECT DESCRIPTION
-----------------------------------------------------------
CureSense is an intelligent healthcare application that leverages AI to analyze symptoms and provide medical insights. 
It predicts diseases, suggests medications, and recommends specialists through an interactive web interface. 
Using Flask APIs for backend and Streamlit for the frontend, CureSense provides a complete AI-driven medical assistance system with features like voice input, smart health advisory, and secure authentication.

