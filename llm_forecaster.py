"""
LLM-based forecasting using OpenAI.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def format_sales_data(product_name: str, category: str, sales_history: List[int], months: int) -> str:
    """Format the sales data for the LLM prompt."""
    return f"""
Product: {product_name}
Category: {category}
Monthly Sales History (oldest to newest): {', '.join(map(str, sales_history))}
"""

def generate_llm_forecast(
    product_name: str, 
    category: str, 
    sales_history: List[int], 
    forecast_months: int = 1
) -> Dict[str, Any]:
    """
    Generate sales forecast using the LLM.
    
    Args:
        product_name: Name of the product
        category: Product category
        sales_history: List of historical sales values
        forecast_months: Number of months to forecast (1-3)
        
    Returns:
        Dictionary containing forecast values, confidence, trend tag, and reasoning
    """
    # Prepare the context
    context = format_sales_data(product_name, category, sales_history, forecast_months)
    
    # Prepare the prompt
    prompt = f"""You are an expert sales forecaster. Based on the historical sales data provided, 
forecast the next {forecast_months} month(s) of sales for this product.

{context}

Analyze the sales history and provide:
1. Sales forecast for each of the next {forecast_months} month(s) (as numeric values)
2. Confidence score for each forecast (0.0-1.0)
3. Trend tag (one of: rising, declining, volatile, flat, stable)
4. A brief reasoning for your forecast

Respond with a JSON object containing the following keys:
"forecasts": [{{month number, forecast value, confidence}}...],
"trend_tag": string,
"reasoning": string
"""

    # Call OpenAI API
    try:
        completion = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        response_text = completion.choices[0].message.content
        response = json.loads(response_text)
        
        return {
            "forecasts": response["forecasts"],
            "trend_tag": response["trend_tag"],
            "reasoning": response["reasoning"]
        }
    
    except Exception as e:
        print(f"Error generating LLM forecast: {e}")
        # Fallback to simple forecasting
        avg = sum(sales_history) / len(sales_history)
        return {
            "forecasts": [
                {"month": i+1, "forecast_value": avg, "confidence": 0.3} 
                for i in range(forecast_months)
            ],
            "trend_tag": "stable",
            "reasoning": "Error in LLM forecast generation, using average sales as fallback."
        }

def calculate_risk_from_llm_forecast(
    forecast_data: Dict[str, Any], 
    last_sales: float
) -> str:
    """
    Calculate risk indicator based on LLM forecast data.
    
    Args:
        forecast_data: Output from generate_llm_forecast
        last_sales: The most recent sales value
        
    Returns:
        Risk indicator string
    """
    trend_tag = forecast_data["trend_tag"]
    
    # Get first month forecast
    first_forecast = forecast_data["forecasts"][0]["forecast_value"]
    confidence = forecast_data["forecasts"][0]["confidence"]
    
    # Calculate growth rate
    growth_rate = (first_forecast - last_sales) / last_sales if last_sales > 0 else 0
    
    # Determine risk based on trend and growth
    if trend_tag == "rising" and growth_rate > 0.15 and confidence > 0.7:
        return "possible stockout"
    elif trend_tag == "declining" and growth_rate < -0.1 and confidence > 0.6:
        return "possible excess inventory"
    elif trend_tag == "volatile":
        return "demand volatility risk"
    elif (trend_tag == "flat" or trend_tag == "stable") and confidence > 0.8:
        return "stable demand"
    else:
        return "normal"
