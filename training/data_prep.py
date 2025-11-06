import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

def load_and_preprocess():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "symptoms_dataset.csv")


    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Dataset not found at: {path}")

    # Read dataset
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # First column = disease, rest = symptoms (binary features)
    disease_col = df.columns[0]
    symptom_cols = df.columns[1:]

    print(f"✅ Detected {len(symptom_cols)} symptom columns and disease column '{disease_col}'.")

    # Build input (X) and output (y)
    X = df[symptom_cols]
    y = df[disease_col].apply(lambda x: [x])  # Wrap each disease name in a list for multilabel encoding

    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(y)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    return (X_train, X_test, Y_train, Y_test), mlb
