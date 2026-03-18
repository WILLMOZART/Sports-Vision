import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from config import Config
from models import db


class PredictionService:
    FEATURES = ["possession", "shots", "shots_on_target", "corners", "home_advantage"]

    @staticmethod
    def _load_model():
        with open(Config.MODEL_PATH, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def _load_scaler():
        with open(Config.SCALER_PATH, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def _prepare_features(venue):
        return 1 if venue == "Home" else 0

    @classmethod
    def get_match_data(cls):
        with db.get_connection() as conn:
            matches = conn.execute(f"""
                SELECT {", ".join(cls.FEATURES[:-1])}, 
                       CASE venue WHEN 'Home' THEN 1 ELSE 0 END as home_advantage,
                       CASE result 
                           WHEN 'Win' THEN 2 
                           WHEN 'Draw' THEN 1 
                           ELSE 0 
                       END as outcome
                FROM matches
            """).fetchall()

        if not matches:
            return []

        df = pd.DataFrame(matches, columns=[*cls.FEATURES, "outcome"])
        return df.to_dict("records")

    @classmethod
    def get_training_data(cls):
        matches = cls.get_match_data()

        if not matches or len(matches) < Config.MIN_MATCHES_FOR_PREDICTION:
            return (
                None,
                f"Not enough data (need {Config.MIN_MATCHES_FOR_PREDICTION} matches)",
            )

        df = pd.DataFrame(matches)

        if df.empty or not all(col in df.columns for col in cls.FEATURES):
            return (
                None,
                f"Not enough data (need {Config.MIN_MATCHES_FOR_PREDICTION} matches)",
            )

        X = df[cls.FEATURES]
        y = df["outcome"]

        return X, y

    @classmethod
    def train_model(cls):
        X, y = cls.get_training_data()

        if X is None:
            return None, y

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_scaled, y)

        cv_scores = cross_val_score(
            model, X_scaled, y, cv=min(5, len(X)), scoring="accuracy"
        )

        os.makedirs("data", exist_ok=True)
        with open(Config.MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        with open(Config.SCALER_PATH, "wb") as f:
            pickle.dump(scaler, f)

        accuracy = model.score(X_scaled, y)

        return (
            {
                "model": model,
                "accuracy": accuracy,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "n_samples": len(X),
            },
            f"Model trained! Train: {accuracy * 100:.1f}%, CV: {cv_scores.mean() * 100:.1f}% ± {cv_scores.std() * 100:.1f}%",
        )

    @classmethod
    def predict(cls, possession, shots, shots_on_target, corners, venue="Home"):
        if not os.path.exists(Config.MODEL_PATH):
            return None, "Model not trained"

        model = cls._load_model()
        scaler = cls._load_scaler()

        home_advantage = cls._prepare_features(venue)
        input_data = np.array(
            [[possession, shots, shots_on_target, corners, home_advantage]]
        )
        input_scaled = scaler.transform(input_data)

        prediction = model.predict(input_scaled)[0]
        probabilities = model.predict_proba(input_scaled)[0]

        outcome_map = {0: "Loss", 1: "Draw", 2: "Win"}

        return {
            "prediction": outcome_map[prediction],
            "confidence": round(probabilities[prediction] * 100, 2),
            "probabilities": {
                "Loss": round(probabilities[0] * 100, 2),
                "Draw": round(probabilities[1] * 100, 2),
                "Win": round(probabilities[2] * 100, 2),
            },
        }, None

    @classmethod
    def get_model_info(cls):
        if not os.path.exists(Config.MODEL_PATH):
            return None

        model = cls._load_model()
        scaler = cls._load_scaler()

        X, y = cls.get_training_data()

        if X is not None:
            X_scaled = scaler.transform(X)
            accuracy = model.score(X_scaled, y)
            cv_scores = cross_val_score(
                model, X_scaled, y, cv=min(5, len(X)), scoring="accuracy"
            )

            return {
                "accuracy": accuracy,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "n_samples": len(X),
                "features": cls.FEATURES,
            }

        return None

    @classmethod
    def delete_model(cls):
        for path in [Config.MODEL_PATH, Config.SCALER_PATH]:
            if os.path.exists(path):
                os.remove(path)
