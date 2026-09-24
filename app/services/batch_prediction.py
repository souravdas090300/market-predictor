"""Batch prediction service for scheduled predictions on all assets."""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from ..core import config
from ..models import predict


class BatchPredictionService:
    """Service for batch prediction of all assets on schedule."""
    
    def __init__(self):
        self.batch_results_file = config.ROOT / "data" / "batch_predictions.json"
        self.batch_results_file.parent.mkdir(exist_ok=True)
        self._load_batch_results()
    
    def _load_batch_results(self):
        """Load existing batch prediction results."""
        if self.batch_results_file.exists():
            try:
                with open(self.batch_results_file) as f:
                    self.batch_results = json.load(f)
            except:
                self.batch_results = {}
        else:
            self.batch_results = {}
    
    def _save_batch_results(self):
        """Save batch prediction results."""
        with open(self.batch_results_file, 'w') as f:
            json.dump(self.batch_results, f, indent=2)
    
    def predict_all_assets(self, force_refresh: bool = False) -> Dict:
        """
        Predict all assets in the watchlist.
        
        Args:
            force_refresh: Force refresh even if recent prediction exists
        
        Returns:
            Dictionary with prediction results for all assets
        """
        results = {}
        timestamp = datetime.utcnow().isoformat()
        
        for asset in config.WATCHLIST:
            symbol = asset["symbol"]
            
            # Check if recent prediction exists (within 1 hour)
            if not force_refresh and symbol in self.batch_results:
                last_prediction = self.batch_results[symbol].get("timestamp")
                if last_prediction:
                    last_time = datetime.fromisoformat(last_prediction)
                    if datetime.utcnow() - last_time < timedelta(hours=1):
                        results[symbol] = self.batch_results[symbol]
                        continue
            
            try:
                # Get prediction
                signal_data = predict.get_signal(symbol, use_news=True, refresh=force_refresh)
                
                # Store result
                self.batch_results[symbol] = {
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "name": asset["name"],
                    "class": asset["class"],
                    "signal": signal_data["signal"],
                    "probability_up": signal_data["probability_up"],
                    "model_probability_up": signal_data["model_probability_up"],
                    "sentiment": signal_data["sentiment"],
                    "indicators": signal_data["indicators"],
                    "candle_patterns": signal_data["candle_patterns"][:5],  # Last 5 patterns
                    "conviction": signal_data["conviction"]
                }
                
                results[symbol] = self.batch_results[symbol]
                
            except Exception as e:
                print(f"Error predicting {symbol}: {e}")
                results[symbol] = {
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "error": str(e)
                }
        
        # Save results
        self._save_batch_results()
        
        return {
            "timestamp": timestamp,
            "total_assets": len(config.WATCHLIST),
            "successful_predictions": len([r for r in results.values() if "error" not in r]),
            "failed_predictions": len([r for r in results.values() if "error" in r]),
            "results": results
        }
    
    def get_prediction_history(self, symbol: str, days: int = 90) -> List[Dict]:
        """
        Get historical predictions for a symbol.
        
        Args:
            symbol: Asset symbol
            days: Number of days of history to retrieve
        
        Returns:
            List of historical predictions
        """
        # For now, return current prediction
        # In production, you'd want to store historical predictions
        if symbol in self.batch_results:
            return [self.batch_results[symbol]]
        return []
    
    def get_aggregate_metrics(self, days: int = 90) -> Dict:
        """
        Get aggregate metrics across all predictions.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with aggregate metrics
        """
        if not self.batch_results:
            return {
                "total_assets": 0,
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "average_conviction": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        total_conviction = 0.0
        valid_predictions = 0
        
        for symbol, data in self.batch_results.items():
            if "error" in data:
                continue
            
            signal = data.get("signal")
            conviction = data.get("conviction", 0.0)
            
            if signal == "bullish":
                bullish_count += 1
            elif signal == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1
            
            total_conviction += conviction
            valid_predictions += 1
        
        average_conviction = total_conviction / valid_predictions if valid_predictions > 0 else 0.0
        
        return {
            "total_assets": len(self.batch_results),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "average_conviction": round(average_conviction, 3),
            "valid_predictions": valid_predictions,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def schedule_predictions(self, interval_hours: int = 1):
        """
        Schedule automatic predictions at regular intervals.
        
        Args:
            interval_hours: Interval in hours between predictions
        """
        import schedule
        import time
        
        def job():
            print(f"Running batch prediction at {datetime.utcnow()}")
            self.predict_all_assets(force_refresh=True)
            print(f"Batch prediction completed at {datetime.utcnow()}")
        
        schedule.every(interval_hours).hours.do(job)
        
        print(f"Scheduled batch predictions every {interval_hours} hours")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


# Global batch prediction service
batch_service = BatchPredictionService()


def run_batch_prediction(force_refresh: bool = False) -> Dict:
    """Run batch prediction for all assets."""
    return batch_service.predict_all_assets(force_refresh=force_refresh)


def get_batch_status() -> Dict:
    """Get current batch prediction status."""
    return batch_service.get_aggregate_metrics()


def get_asset_prediction(symbol: str) -> Optional[Dict]:
    """Get batch prediction for a specific asset."""
    return batch_service.batch_results.get(symbol)