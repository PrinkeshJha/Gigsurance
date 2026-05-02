import os
import joblib
import random
import logging
from typing import Dict, Any
from sklearn.ensemble import RandomForestRegressor
import numpy as np

logger = logging.getLogger("gigsurance-backend")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.joblib")

_model = None

# City Risk mapping (for simple encoding)
CITY_RISK_MAP = {
    "delhi": 2.0, "jaipur": 1.8, "ahmedabad": 1.7,
    "mumbai": 1.5, "kolkata": 1.4, "chennai": 1.4,
    "bangalore": 1.2, "hyderabad": 1.2,
}

SEASON_MAP = {
    "Spring": 1, "Summer": 2, "Monsoon": 3, "Winter": 0
}

def _get_season_encoded(season_str: str) -> int:
    return SEASON_MAP.get(season_str, 0)

def parse_working_hours(working_hours: str) -> int:
    try:
        if not working_hours or "-" not in working_hours:
            return 8
        start_str, end_str = working_hours.split("-")
        start_hour = int(start_str.split(":")[0])
        end_hour = int(end_str.split(":")[0])
        return max(1, end_hour - start_hour)
    except Exception:
        return 8

def train_model():
    """
    Train a synthetic RandomForestRegressor model and save to disk.
    Features: [avg_temp, rain_freq, working_hours, season_enc, city_risk]
    Target: risk_score (0.5 to 2.5)
    """
    logger.info("Training AI risk scoring model with synthetic data...")
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR, exist_ok=True)
        
    X = []
    y = []
    
    # Generate 1000 synthetic samples
    for _ in range(1000):
        temp = random.uniform(20.0, 48.0)
        rain = random.uniform(0.0, 20.0) # mm/hr
        hours = random.randint(4, 14)
        season = random.choice(list(SEASON_MAP.values()))
        city_risk = random.uniform(1.0, 2.0)
        
        # Determine risk
        risk = 1.0
        if temp > 40: risk += 0.5
        if rain > 10: risk += 0.4
        if hours > 10: risk += 0.3
        risk += (city_risk - 1.0) * 0.5
        if season in [2, 3]: risk += 0.2
        
        risk = max(0.5, min(2.5, risk))
        
        X.append([temp, rain, hours, season, city_risk])
        y.append(risk)
        
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            logger.warning("Risk model not found. Training a new one...")
            train_model()
        _model = joblib.load(MODEL_PATH)
        logger.info("Risk model loaded successfully.")
    return _model

def calculate_risk_score(user_data: Dict[str, Any]) -> float:
    """
    Calculate risk score using ML model.
    """
    try:
        model = load_model()
        
        city = user_data.get("city", "").lower()
        city_risk = CITY_RISK_MAP.get(city, 1.0)
        working_hours = parse_working_hours(user_data.get("working_hours", "09:00-18:00"))
        
        # Simple defaults for missing dynamic weather data during onboarding
        avg_temp = user_data.get("avg_temp", 30.0)
        rain_freq = user_data.get("rain_freq", 5.0)
        season_enc = user_data.get("season", 1)  # Default Spring
        
        features = np.array([[avg_temp, rain_freq, working_hours, season_enc, city_risk]])
        
        score = model.predict(features)[0]
        
        # Ensure it's between 0.5 and 2.5
        return round(float(max(0.5, min(2.5, score))), 2)
        
    except Exception as e:
        logger.error(f"Error calculating AI risk score: {e}")
        return 1.0
