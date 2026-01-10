import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = os.environ.get("AIP_MODEL_DIR", "/tmp/model")

def main():
    df = pd.read_csv("data/training_data.csv")

    # Feature engineering
    df["days_since_due"] = (pd.Timestamp.today() - pd.to_datetime(df["due_date"])).dt.days
    df["days_since_handover"] = (pd.Timestamp.today() - pd.to_datetime(df["handover_date"])).dt.days
    df["credit_utilization"] = df["invoice_amount"] / df["credit_limit"]
    df["late_ratio"] = df["late_payments"] / df["total_payments"].replace(0, 1)
    df["payment_consistency"] = df["payments_paid"] / df["total_payments"].replace(0, 1)

    features = [
        "invoice_amount",
        "days_since_due",
        "days_since_handover",
        "credit_utilization",
        "late_ratio",
        "payment_consistency"
    ]

    X = df[features]

    le = LabelEncoder()
    y = le.fit_transform(df["collection_risk"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss"
    )

    model.fit(X_train, y_train)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, f"{MODEL_DIR}/risk_model.joblib")
    joblib.dump(le, f"{MODEL_DIR}/label_encoder.joblib")

    print("Risk model trained and saved")

if __name__ == "__main__":
    main()
