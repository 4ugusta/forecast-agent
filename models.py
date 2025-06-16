"""
Models for the Forecast Agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """Product data model."""
    product_id: int
    product_name: str
    category: str
    sales_history: List[int]
    trend_score: float


class ForecastResult(BaseModel):
    """Forecast result model."""
    product_id: int
    product_name: str
    category: str
    forecast_value: float
    confidence_score: float
    trend_tag: str
    risk_indicator: str
    narrative: str
    forecast_months: int = 1


class AgentResponse(BaseModel):
    """Response from the agent system."""
    forecasts: List[ForecastResult]
    summary: str
    timestamp: str
