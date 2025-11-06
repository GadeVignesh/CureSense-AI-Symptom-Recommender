import numpy as np
import pandas as pd
import re
from joblib import load
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/model.pkl")
MLB_PATH = os.path.join(BASE_DIR, "../models/mlb.pkl")

model = load(MODEL_PATH)
mlb = load(MLB_PATH)

def preprocess_text(text: str) -> list:
    """Convert input text into clean symptom tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z,\s]", "", text)
    symptoms = [s.strip() for s in text.split(",") if s.strip()]
    return symptoms

def predict_diseases(symptom_text: str, top_k=3):
    """Predict top diseases for given symptoms."""
    symptoms = preprocess_text(symptom_text)

    feature_names = model.estimators_[0].feature_names_in_
    input_vector = np.zeros(len(feature_names))

    for i, s in enumerate(feature_names):
        if s in symptoms:
            input_vector[i] = 1

    import pandas as pd
    input_df = pd.DataFrame([input_vector], columns=feature_names)

    probs = model.predict_proba(input_df)[0]
    classes = mlb.classes_

    top_indices = np.argsort(probs)[::-1][:top_k]
    top_diseases = [(classes[i], round(float(probs[i]) * 100, 2)) for i in top_indices if probs[i] > 0.01]

    return top_diseases

DISEASE_MED_MAP = {
    "flu": {"meds": ["Paracetamol", "Rest", "Fluids"], "doctors": ["General Physician"]},
    "common cold": {"meds": ["Antihistamine", "Cough Syrup"], "doctors": ["ENT Specialist"]},
    "migraine": {"meds": ["Ibuprofen", "Pain Relievers"], "doctors": ["Neurologist"]},
    "conjunctivitis": {"meds": ["Antibiotic Eye Drops", "Warm Compress"], "doctors": ["Ophthalmologist"]},
    "otitis externa (swimmer's ear)": {"meds": ["Antibiotic Ear Drops", "Pain Relievers"], "doctors": ["ENT Specialist"]},
    "oral mucosal lesion": {"meds": ["Mouth Gel", "Vitamin B Complex", "Saltwater Gargle"], "doctors": ["Dentist", "Oral Surgeon"]},
    "vitamin d deficiency": {"meds": ["Vitamin D Supplements", "Sunlight Exposure"], "doctors": ["Endocrinologist"]},
    "anemia": {"meds": ["Iron Supplements", "Folic Acid", "Vitamin B12"], "doctors": ["Hematologist"]},
    "asthma": {"meds": ["Inhaler (Salbutamol)", "Steroids"], "doctors": ["Pulmonologist"]},
    "diabetes": {"meds": ["Metformin", "Insulin"], "doctors": ["Endocrinologist"]},
    "hypertension": {"meds": ["Amlodipine", "Lifestyle Modification"], "doctors": ["Cardiologist"]},
    "skin infection": {"meds": ["Antibiotic Cream", "Antifungal Cream"], "doctors": ["Dermatologist"]},
}

DEFAULT_CATEGORY_MAP = {
    "eye": {"meds": ["Lubricating Drops", "Cold Compress"], "doctors": ["Ophthalmologist"]},
    "ear": {"meds": ["Ear Drops", "Pain Relievers"], "doctors": ["ENT Specialist"]},
    "throat": {"meds": ["Antibiotic", "Gargle with Salt Water"], "doctors": ["ENT Specialist"]},
    "skin": {"meds": ["Antifungal Cream", "Moisturizer"], "doctors": ["Dermatologist"]},
    "stomach": {"meds": ["Antacid", "Hydration", "Light Diet"], "doctors": ["Gastroenterologist"]},
    "respiratory": {"meds": ["Cough Syrup", "Steam Inhalation"], "doctors": ["Pulmonologist"]},
    "fever": {"meds": ["Paracetamol", "Rest", "Fluids"], "doctors": ["General Physician"]},
}


def recommend_for_diseases(disease_list):
    meds, docs = set(), set()

    for d, _ in disease_list:
        disease = d.lower().strip()

        if disease in DISEASE_MED_MAP:
            info = DISEASE_MED_MAP[disease]
            meds.update(info["meds"])
            docs.update(info["doctors"])
            continue

        for key, info in DEFAULT_CATEGORY_MAP.items():
            if key in disease:
                meds.update(info["meds"])
                docs.update(info["doctors"])
                break

        if not any(key in disease for key in DEFAULT_CATEGORY_MAP.keys()):
            meds.update(["Consult Doctor", "Hydration", "Rest"])
            docs.update(["General Physician"])

    return sorted(meds), sorted(docs)
