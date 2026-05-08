import os
import joblib
import numpy as np
import logging

logger = logging.getLogger("gigsurance-backend.ml-fraud")

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'fraud_model.joblib')

class MLFraudDetector:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                logger.info("ML Fraud detection model loaded successfully.")
            else:
                logger.warning(f"ML Fraud model not found at {MODEL_PATH}. Run training script.")
        except Exception as e:
            logger.error(f"Failed to load ML Fraud model: {e}")
            
    def detect_fraud(self, user_features: dict) -> dict:
        """
        user_features dict must contain:
        claims_per_week, avg_payout_amount, avg_distance_from_trigger_zone,
        gps_update_frequency, payout_frequency, trigger_count,
        working_hours, unusual_activity_score
        """
        if not self.model:
            # Safe fallback if model is unavailable
            return {"status": "normal", "anomaly_score": 0.0}
            
        try:
            # Extract features in exact training order
            features = [
                float(user_features.get("claims_per_week", 0.0)),
                float(user_features.get("avg_payout_amount", 0.0)),
                float(user_features.get("avg_distance_from_trigger_zone", 0.0)),
                float(user_features.get("gps_update_frequency", 20.0)),
                float(user_features.get("payout_frequency", 0.1)),
                float(user_features.get("trigger_count", 0.0)),
                float(user_features.get("working_hours", 8.0)),
                float(user_features.get("unusual_activity_score", 0.0))
            ]
            
            X = np.array([features])
            
            # predict returns 1 for inliers, -1 for outliers
            prediction = self.model.predict(X)[0]
            
            # decision_function returns anomaly score (lower is more abnormal)
            score = self.model.decision_function(X)[0]
            
            # Normalize score to 0-1 range for easier interpretation (approximate)
            normalized_score = float(np.clip(0.5 - score, 0.0, 1.0))
            
            status = "suspicious" if prediction == -1 else "normal"
            
            return {
                "status": status,
                "anomaly_score": normalized_score
            }
        except Exception as e:
            logger.error(f"Error during ML fraud detection: {e}")
            return {"status": "normal", "anomaly_score": 0.0}

# Singleton instance
fraud_detector = MLFraudDetector()

def detect_fraud(user_features: dict) -> dict:
    return fraud_detector.detect_fraud(user_features)
