"""Prediction accuracy tracking system."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from . import config

# In-memory storage for predictions
_predictions: Dict[str, List[dict]] = {}

# File path for persistence
_ACCURACY_FILE = config.DATA / "prediction_accuracy.json"


def load_accuracy_data():
    """Load accuracy data from file."""
    try:
        if _ACCURACY_FILE.exists():
            with open(_ACCURACY_FILE, 'r') as f:
                data = json.load(f)
                _predictions.update(data)
    except Exception:
        pass


def save_accuracy_data():
    """Save accuracy data to file."""
    try:
        _ACCURACY_FILE.parent.mkdir(exist_ok=True)
        with open(_ACCURACY_FILE, 'w') as f:
            json.dump(_predictions, f, indent=2)
    except Exception:
        pass


def record_prediction(
    symbol: str,
    horizon: str,
    predicted_direction: str,
    predicted_price: float,
    current_price: float,
    confidence: float
):
    """Record a prediction for later accuracy calculation."""
    key = f"{symbol.lower()}_{horizon}"
    
    if key not in _predictions:
        _predictions[key] = []
    
    prediction = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "horizon": horizon,
        "predicted_direction": predicted_direction,
        "predicted_price": predicted_price,
        "current_price": current_price,
        "confidence": confidence,
        "outcome": None,  # Will be set when we check the result
        "actual_price": None,
        "correct": None
    }
    
    _predictions[key].append(prediction)
    save_accuracy_data()


def check_prediction_outcome(symbol: str, horizon: str, prediction_time: str):
    """Check if a prediction was correct based on actual price movement."""
    try:
        from . import data
        
        key = f"{symbol.lower()}_{horizon}"
        
        if key not in _predictions:
            return None
        
        # Find the prediction
        pred = None
        for p in _predictions[key]:
            if p["timestamp"] == prediction_time and p["outcome"] is None:
                pred = p
                break
        
        if not pred:
            return None
        
        # Get current price
        quote = data.get_live_quote(symbol)
        if not quote:
            return None
        
        actual_price = quote["price"]
        pred["actual_price"] = actual_price
        
        # Determine if prediction was correct
        if pred["predicted_direction"] == "up":
            pred["correct"] = actual_price > pred["current_price"]
        elif pred["predicted_direction"] == "down":
            pred["correct"] = actual_price < pred["current_price"]
        else:
            pred["correct"] = abs(actual_price - pred["predicted_price"]) / pred["predicted_price"] < 0.01
        
        pred["outcome"] = "correct" if pred["correct"] else "incorrect"
        
        save_accuracy_data()
        return pred
    except Exception:
        return None


def get_accuracy_stats(symbol: str, horizon: str = None) -> dict:
    """Get accuracy statistics for a symbol (and optionally specific horizon)."""
    key_prefix = f"{symbol.lower()}_"
    
    total_predictions = 0
    correct_predictions = 0
    horizon_stats = {}
    
    for key, predictions in _predictions.items():
        if not key.startswith(key_prefix):
            continue
        
        if horizon and not key.endswith(f"_{horizon}"):
            continue
        
        for pred in predictions:
            if pred["outcome"] is not None:
                total_predictions += 1
                if pred["correct"]:
                    correct_predictions += 1
                
                # Track by horizon
                h = pred["horizon"]
                if h not in horizon_stats:
                    horizon_stats[h] = {"total": 0, "correct": 0}
                horizon_stats[h]["total"] += 1
                if pred["correct"]:
                    horizon_stats[h]["correct"] += 1
    
    accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else None
    
    # Calculate accuracy per horizon
    horizon_accuracy = {}
    for h, stats in horizon_stats.items():
        if stats["total"] > 0:
            horizon_accuracy[h] = {
                "accuracy": round(stats["correct"] / stats["total"] * 100, 2),
                "total_predictions": stats["total"],
                "correct_predictions": stats["correct"]
            }
    
    return {
        "symbol": symbol,
        "overall_accuracy": round(accuracy, 2) if accuracy else None,
        "total_predictions": total_predictions,
        "correct_predictions": correct_predictions,
        "horizon_accuracy": horizon_accuracy,
        "sample_size": total_predictions
    }


def get_simulated_accuracy(symbol: str, horizon: str) -> float:
    """Get simulated accuracy for demonstration (will be replaced with real data)."""
    # In production, this would use real historical accuracy
    # For now, return realistic values based on asset class and horizon
    
    # Base accuracy by horizon (shorter = harder)
    base_accuracy = {
        "1h": 52.0,
        "2h": 53.0,
        "3h": 53.5,
        "4h": 54.0,
        "5h": 54.0,
        "6h": 54.5,
        "8h": 55.0,
        "12h": 56.0,
        "24h": 58.0,
        "7d": 62.0,
        "30d": 65.0
    }
    
    base = base_accuracy.get(horizon, 55.0)
    
    # Add some randomness based on symbol hash
    import random
    random.seed(hash(symbol + horizon) % 1000)
    variation = random.uniform(-3.0, 3.0)
    
    # Crypto is more volatile, slightly lower accuracy
    if "-" in symbol.upper():  # Crypto symbols usually have hyphen
        variation -= 1.0
    
    accuracy = base + variation
    return round(max(45.0, min(75.0, accuracy)), 2)


# Load data on module import
load_accuracy_data()
