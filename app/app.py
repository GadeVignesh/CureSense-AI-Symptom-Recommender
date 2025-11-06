from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db import init_db, SessionLocal, User, History
from app.utils import predict_diseases, recommend_for_diseases
from app.auth import bp as auth_bp, TOKENS
import json

app = Flask(__name__)
CORS(app)  # ✅ Enables frontend (Streamlit) to access backend safely
app.register_blueprint(auth_bp, url_prefix="/auth")

# Initialize database
init_db()

# ✅ Root route to avoid "Not Found" error
@app.route('/')
def home():
    return jsonify({
        "message": "✅ CureSense Flask Backend is Live!",
        "status": "running",
        "endpoints": ["/health", "/predict", "/history", "/auth"]
    })

# ✅ Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# ✅ Disease prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    symptoms = data.get('symptoms', '')
    token = request.headers.get('Authorization')

    if not symptoms:
        return jsonify({'error': 'No symptoms provided'}), 400

    disease_confidences = predict_diseases(symptoms)
    diseases_only = [d for d, _ in disease_confidences]
    meds, docs = recommend_for_diseases(disease_confidences)

    username = TOKENS.get(token)
    db = SessionLocal()
    if username:
        user = db.query(User).filter_by(username=username).first()
        if user:
            hist = History(
                user_id=user.id,
                symptoms=symptoms,
                predicted_diseases=json.dumps(diseases_only),
                medications=json.dumps(meds)
            )
            db.add(hist)
            db.commit()

    return jsonify({
        'symptoms': symptoms,
        'predicted_diseases': disease_confidences,
        'medications': meds,
        'doctor_types': docs
    })

# ✅ User history endpoint
@app.route('/history', methods=['GET'])
def history():
    token = request.headers.get('Authorization')
    username = TOKENS.get(token)

    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    records = db.query(History).filter_by(user_id=user.id).order_by(History.created_at.desc()).all()
    history = [
        {
            'symptoms': h.symptoms,
            'predicted_diseases': json.loads(h.predicted_diseases),
            'medications': json.loads(h.medications),
            'created_at': h.created_at.isoformat()
        }
        for h in records
    ]
    return jsonify({'user': username, 'history': history})

# ✅ Run the app (Render uses Gunicorn, but this is for local testing)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
