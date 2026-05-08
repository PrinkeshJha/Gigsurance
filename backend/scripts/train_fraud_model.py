import os
import sys
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic feature data for GigSurance workers.
    Features:
    0. claims_per_week: normal 0-2, fraud 3-10
    1. avg_payout_amount: normal 100-500, fraud 500-2000
    2. avg_distance_from_trigger_zone: normal 0-5, fraud 5-50
    3. gps_update_frequency (updates per day): normal 10-50, fraud 0-5
    4. payout_frequency: normal 0.1-0.3, fraud 0.5-1.0
    5. trigger_count: normal 1-5, fraud 5-20
    6. working_hours: normal 4-12, fraud 1-2 or 18-24
    7. unusual_activity_score: normal 0-0.3, fraud 0.7-1.0
    """
    np.random.seed(42)
    
    # Normal data (90%)
    n_normal = int(n_samples * 0.9)
    normal_data = np.column_stack([
        np.random.uniform(0, 2, n_normal),
        np.random.uniform(100, 500, n_normal),
        np.random.uniform(0, 5, n_normal),
        np.random.uniform(10, 50, n_normal),
        np.random.uniform(0.1, 0.3, n_normal),
        np.random.uniform(1, 5, n_normal),
        np.random.uniform(4, 12, n_normal),
        np.random.uniform(0, 0.3, n_normal)
    ])
    
    # Fraud data (10%)
    n_fraud = n_samples - n_normal
    fraud_data = np.column_stack([
        np.random.uniform(3, 10, n_fraud),
        np.random.uniform(500, 2000, n_fraud),
        np.random.uniform(5, 50, n_fraud),
        np.random.uniform(0, 5, n_fraud),
        np.random.uniform(0.5, 1.0, n_fraud),
        np.random.uniform(5, 20, n_fraud),
        np.random.uniform(18, 24, n_fraud), # Assuming fraud claims absurd hours
        np.random.uniform(0.7, 1.0, n_fraud)
    ])
    
    return np.vstack([normal_data, fraud_data])

def train_model():
    print("Generating synthetic data...")
    X = generate_synthetic_data(2000)
    
    print("Training IsolationForest model...")
    # contamination is the expected proportion of outliers
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)
    
    # Ensure models dir exists
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'fraud_model.joblib')
    joblib.dump(model, model_path)
    
    print(f"Model saved successfully to {model_path}")

if __name__ == "__main__":
    train_model()
