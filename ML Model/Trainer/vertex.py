import joblib
import numpy as np

model = joblib.load("risk_model.joblib")
encoder = joblib.load("label_encoder.joblib")

def predict_risk(features: dict):
    X = np.array([[
        features["invoice_amount"],
        features["days_since_due"],
        features["days_since_handover"],
        features["credit_utilization"],
        features["late_ratio"],
        features["payment_consistency"]
    ]])

    probs = model.predict_proba(X)[0]
    label = encoder.inverse_transform([np.argmax(probs)])[0]

    return {
        "collection_risk": label,
        "confidence": float(np.max(probs))
    }
