"""
Utility functions for forecasting.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Tuple, Dict, Any


def calculate_statistical_forecast(sales_history: List[int], periods: int = 1) -> List[float]:
    """
    Calculate forecast using statistical methods.
    
    Args:
        sales_history: List of historical sales values
        periods: Number of periods to forecast
        
    Returns:
        List of forecasted values
    """
    if len(sales_history) < 4:
        # Not enough data for statistical forecasting, use simple average
        avg = sum(sales_history) / len(sales_history)
        return [avg for _ in range(periods)]
    
    try:
        # Try ARIMA model first
        model = ARIMA(sales_history, order=(1, 0, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=periods)
        return list(forecast)
    except:
        # Fallback to simple linear regression
        X = np.array(range(len(sales_history))).reshape(-1, 1)
        y = np.array(sales_history)
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next periods
        X_pred = np.array(range(len(sales_history), len(sales_history) + periods)).reshape(-1, 1)
        predictions = model.predict(X_pred)
        
        # Ensure no negative values
        return [max(0, float(pred)) for pred in predictions]


def calculate_confidence_score(sales_history: List[int]) -> float:
    """
    Calculate confidence score based on consistency and trend strength.
    
    Args:
        sales_history: List of historical sales values
        
    Returns:
        Confidence score between 0 and 1
    """
    # If sales history is too short, return moderate confidence
    if len(sales_history) < 3:
        return 0.5
    
    # Calculate coefficient of variation (normalized measure of dispersion)
    mean = np.mean(sales_history)
    std = np.std(sales_history)
    cv = std / mean if mean > 0 else float('inf')
    
    # Calculate trend strength (R-squared of linear regression)
    X = np.array(range(len(sales_history))).reshape(-1, 1)
    y = np.array(sales_history)
    model = LinearRegression()
    model.fit(X, y)
    r_squared = model.score(X, y)
    
    # Combine metrics - lower variability and stronger trend means higher confidence
    consistency_score = max(0, min(1, 1 - (cv / 2)))
    confidence = (consistency_score + r_squared) / 2
    
    return round(confidence, 2)


def determine_trend_tag(sales_history: List[int], forecast: float) -> str:
    """
    Determine trend tag based on recent sales pattern.
    
    Args:
        sales_history: List of historical sales values
        forecast: Forecasted value for next period
        
    Returns:
        Trend tag string
    """
    if len(sales_history) < 3:
        return "insufficient data"
        
    # Calculate recent trend
    recent_sales = sales_history[-3:]
    avg_change = sum(recent_sales[i] - recent_sales[i-1] for i in range(1, len(recent_sales))) / (len(recent_sales) - 1)
    
    # Calculate volatility
    volatility = np.std(sales_history) / np.mean(sales_history) if np.mean(sales_history) > 0 else 0
    
    # Check if forecast is higher than last period
    forecast_change = forecast - sales_history[-1]
    forecast_change_pct = forecast_change / sales_history[-1] if sales_history[-1] > 0 else 0
    
    # Determine tag based on trend and volatility
    if volatility > 0.2:
        return "volatile"
    elif forecast_change_pct > 0.1:
        return "rising"
    elif forecast_change_pct < -0.1:
        return "declining"
    elif abs(forecast_change_pct) <= 0.05:
        return "flat"
    else:
        return "stable"


def determine_risk_indicator(sales_history: List[int], forecast: float, trend_score: float) -> str:
    """
    Determine risk indicator based on forecast and trend.
    
    Args:
        sales_history: List of historical sales values
        forecast: Forecasted value for next period
        trend_score: Pre-calculated trend score (0-1)
        
    Returns:
        Risk indicator string
    """
    if len(sales_history) < 2:
        return "unknown"
    
    # Calculate growth rate
    last_period = sales_history[-1]
    growth_rate = (forecast - last_period) / last_period if last_period > 0 else 0
    
    # High trend score with significant growth suggests possible stockout
    if trend_score > 0.6 and growth_rate > 0.15:
        return "possible stockout"
    
    # Declining sales might indicate excess inventory
    elif growth_rate < -0.1:
        return "possible excess inventory"
    
    # Volatile sales pattern
    elif np.std(sales_history) / np.mean(sales_history) > 0.25 if np.mean(sales_history) > 0 else False:
        return "demand volatility risk"
    
    # Stable sales with high trend score
    elif trend_score > 0.7 and abs(growth_rate) < 0.05:
        return "stable demand"
    
    # Default case
    else:
        return "normal"
