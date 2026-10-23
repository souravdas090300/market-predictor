"""
Gemini AI Service for Market Predictions
Uses Google's Gemini API for free AI-powered market analysis
"""

import os
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Gemini AI features will be disabled.")


class GeminiAIService:
    """Service for Gemini AI-powered market predictions and analysis."""

    def __init__(self):
        """Initialize Gemini AI service."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.enabled = False

        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.enabled = True
                logger.info("Gemini AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("google-generativeai package not installed")
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not set in environment")

    def is_available(self) -> bool:
        """Check if Gemini AI service is available."""
        return self.enabled

    async def analyze_market_sentiment(
        self,
        symbol: str,
        news_headlines: List[str],
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment using Gemini AI.

        Args:
            symbol: Asset symbol (e.g., AAPL, BTC-USD)
            news_headlines: List of recent news headlines
            additional_context: Additional context about the asset

        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.enabled:
            return self._fallback_sentiment(symbol, news_headlines)

        try:
            prompt = f"""
            Analyze the market sentiment for {symbol} based on the following news headlines:

            {json.dumps(news_headlines, indent=2)}

            {additional_context}

            Provide your analysis in the following JSON format:
            {{
                "overall_sentiment": "bullish" or "bearish" or "neutral",
                "sentiment_score": 0.0 to 1.0,
                "confidence": 0.0 to 1.0,
                "key_factors": ["factor1", "factor2", ...],
                "risk_level": "low" or "medium" or "high",
                "short_term_outlook": "positive" or "negative" or "neutral",
                "summary": "Brief summary of your analysis"
            }}
            """

            response = await self.model.generate_content_async(prompt)
            result_text = response.text

            # Parse JSON from response
            try:
                # Extract JSON from response (in case there's extra text)
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result_text = result_text[json_start:json_end]

                result = json.loads(result_text)
                return {
                    "source": "gemini_ai",
                    "symbol": symbol,
                    **result
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini AI response: {result_text}")
                return self._fallback_sentiment(symbol, news_headlines)

        except Exception as e:
            logger.error(f"Error in Gemini AI sentiment analysis: {e}")
            return self._fallback_sentiment(symbol, news_headlines)

    async def predict_price_movement(
        self,
        symbol: str,
        historical_data: List[Dict[str, Any]],
        time_horizon: str = "24h"
    ) -> Dict[str, Any]:
        """
        Predict price movement using Gemini AI.

        Args:
            symbol: Asset symbol
            historical_data: Historical price data
            time_horizon: Prediction horizon (1h, 4h, 24h, 7d, 30d)

        Returns:
            Dictionary with prediction results
        """
        if not self.enabled:
            return self._fallback_prediction(symbol, time_horizon)

        try:
            # Prepare data summary
            recent_prices = [d.get("close", 0) for d in historical_data[-10:]]
            price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100 if recent_prices else 0

            prompt = f"""
            Based on the following historical price data for {symbol}:

            Recent prices (last 10 periods): {recent_prices}
            Recent change: {price_change:.2f}%

            Predict the price movement for the next {time_horizon}.

            Provide your prediction in the following JSON format:
            {{
                "direction": "up" or "down" or "neutral",
                "predicted_change_percent": -100.0 to 100.0,
                "confidence": 0.0 to 1.0,
                "support_level": price value,
                "resistance_level": price value,
                "key_indicators": ["indicator1", "indicator2", ...],
                "risk_assessment": "low" or "medium" or "high",
                "reasoning": "Brief explanation of your prediction"
            }}
            """

            response = await self.model.generate_content_async(prompt)
            result_text = response.text

            # Parse JSON from response
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result_text = result_text[json_start:json_end]

                result = json.loads(result_text)
                return {
                    "source": "gemini_ai",
                    "symbol": symbol,
                    "time_horizon": time_horizon,
                    **result
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini AI prediction: {result_text}")
                return self._fallback_prediction(symbol, time_horizon)

        except Exception as e:
            logger.error(f"Error in Gemini AI price prediction: {e}")
            return self._fallback_prediction(symbol, time_horizon)

    async def generate_trading_strategy(
        self,
        symbol: str,
        risk_tolerance: str = "moderate",
        investment_horizon: str = "medium-term"
    ) -> Dict[str, Any]:
        """
        Generate a trading strategy using Gemini AI.

        Args:
            symbol: Asset symbol
            risk_tolerance: low, moderate, or high
            investment_horizon: short-term, medium-term, or long-term

        Returns:
            Dictionary with trading strategy recommendations
        """
        if not self.enabled:
            return self._fallback_strategy(symbol, risk_tolerance)

        try:
            prompt = f"""
            Generate a trading strategy for {symbol} with the following parameters:
            - Risk tolerance: {risk_tolerance}
            - Investment horizon: {investment_horizon}

            Provide your strategy in the following JSON format:
            {{
                "strategy_name": "Descriptive name",
                "entry_conditions": ["condition1", "condition2", ...],
                "exit_conditions": ["condition1", "condition2", ...],
                "position_size_percent": 0 to 100,
                "stop_loss_percent": 0 to 100,
                "take_profit_percent": 0 to 100,
                "risk_reward_ratio": 0.0 to 10.0,
                "key_indicators": ["indicator1", "indicator2", ...],
                "expected_win_rate": 0.0 to 1.0,
                "notes": "Additional notes and considerations"
            }}
            """

            response = await self.model.generate_content_async(prompt)
            result_text = response.text

            # Parse JSON from response
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result_text = result_text[json_start:json_end]

                result = json.loads(result_text)
                return {
                    "source": "gemini_ai",
                    "symbol": symbol,
                    "risk_tolerance": risk_tolerance,
                    "investment_horizon": investment_horizon,
                    **result
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini AI strategy: {result_text}")
                return self._fallback_strategy(symbol, risk_tolerance)

        except Exception as e:
            logger.error(f"Error in Gemini AI strategy generation: {e}")
            return self._fallback_strategy(symbol, risk_tolerance)

    def _fallback_sentiment(self, symbol: str, news_headlines: List[str]) -> Dict[str, Any]:
        """Fallback sentiment analysis when Gemini is unavailable."""
        positive_count = sum(1 for h in news_headlines if any(word in h.lower() for word in ['up', 'gain', 'rise', 'growth', 'positive', 'bull']))
        negative_count = sum(1 for h in news_headlines if any(word in h.lower() for word in ['down', 'loss', 'fall', 'decline', 'negative', 'bear']))

        total = len(news_headlines) or 1
        sentiment_score = (positive_count - negative_count) / total
        sentiment_score = max(0, min(1, (sentiment_score + 1) / 2))  # Normalize to 0-1

        return {
            "source": "fallback",
            "symbol": symbol,
            "overall_sentiment": "bullish" if sentiment_score > 0.6 else "bearish" if sentiment_score < 0.4 else "neutral",
            "sentiment_score": sentiment_score,
            "confidence": 0.5,
            "key_factors": ["news analysis"],
            "risk_level": "medium",
            "short_term_outlook": "neutral",
            "summary": "Fallback sentiment analysis (Gemini AI unavailable)"
        }

    def _fallback_prediction(self, symbol: str, time_horizon: str) -> Dict[str, Any]:
        """Fallback price prediction when Gemini is unavailable."""
        import random
        random.seed(hash(symbol + time_horizon) % 1000)

        change = random.uniform(-5, 5)
        direction = "up" if change > 0 else "down" if change < 0 else "neutral"

        return {
            "source": "fallback",
            "symbol": symbol,
            "time_horizon": time_horizon,
            "direction": direction,
            "predicted_change_percent": change,
            "confidence": random.uniform(0.5, 0.7),
            "support_level": None,
            "resistance_level": None,
            "key_indicators": ["fallback analysis"],
            "risk_assessment": "medium",
            "reasoning": "Fallback prediction (Gemini AI unavailable)"
        }

    def _fallback_strategy(self, symbol: str, risk_tolerance: str) -> Dict[str, Any]:
        """Fallback strategy when Gemini is unavailable."""
        risk_configs = {
            "low": {"position": 20, "stop_loss": 5, "take_profit": 10},
            "moderate": {"position": 50, "stop_loss": 10, "take_profit": 20},
            "high": {"position": 80, "stop_loss": 15, "take_profit": 30}
        }

        config = risk_configs.get(risk_tolerance, risk_configs["moderate"])

        return {
            "source": "fallback",
            "symbol": symbol,
            "risk_tolerance": risk_tolerance,
            "investment_horizon": "medium-term",
            "strategy_name": f"Basic {risk_tolerance} Strategy",
            "entry_conditions": ["Price above moving average", "Positive momentum"],
            "exit_conditions": ["Price below stop loss", "Take profit reached"],
            "position_size_percent": config["position"],
            "stop_loss_percent": config["stop_loss"],
            "take_profit_percent": config["take_profit"],
            "risk_reward_ratio": 2.0,
            "key_indicators": ["Moving Average", "RSI"],
            "expected_win_rate": 0.55,
            "notes": "Fallback strategy (Gemini AI unavailable)"
        }


# Global instance
gemini_service = GeminiAIService()
