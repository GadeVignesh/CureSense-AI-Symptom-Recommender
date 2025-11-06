import joblib
import os
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from training.data_prep import load_and_preprocess


def train_and_save():
    """
    Train a multi-label disease prediction model using symptom data,
    then save both the trained model and label binarizer in /models.
    """
    print("🚀 Starting training process...")
    (X_train, X_test, Y_train, Y_test), mlb = load_and_preprocess()
    print(f"✅ Data loaded: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples")

    clf = OneVsRestClassifier(LogisticRegression(max_iter=500, solver="liblinear"))
    print("🧠 Training model... This may take a few minutes depending on dataset size.")
    clf.fit(X_train, Y_train)

    preds = clf.predict(X_test)
    f1 = f1_score(Y_test, preds, average="micro")
    print("\n📊 Evaluation Metrics:")
    print("F1-score (micro):", round(f1, 3))
    print(classification_report(Y_test, preds, target_names=mlb.classes_))

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "model.pkl")
    mlb_path = os.path.join(model_dir, "mlb.pkl")

    joblib.dump(clf, model_path)
    joblib.dump(mlb, mlb_path)

    print(f"\n✅ Model saved to: {model_path}")
    print(f"✅ Label binarizer saved to: {mlb_path}")
    print("🎉 Training and saving completed successfully!")


if __name__ == "__main__":
    train_and_save()
