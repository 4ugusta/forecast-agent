"""
Forecast Agent implementation using CrewAI.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from models import ProductData, ForecastResult, AgentResponse
import forecast_utils as utils

# Import llm_forecaster conditionally when needed
llm_forecaster = None


class ForecastAgentSystem:
    """Main class for the forecast agent system."""
    
    def __init__(self):
        # Initialize agents
        self.forecaster_agent = self._create_forecaster_agent()
        self.risk_agent = self._create_risk_agent()
        self.narrative_agent = self._create_narrative_agent()
        
    def _create_forecaster_agent(self):
        """Create the forecaster agent."""
        return Agent(
            role="Forecaster",
            goal="Accurately predict future sales based on historical data",
            backstory="""You are an expert in time series forecasting with years of 
            experience in retail and e-commerce sales prediction. Your forecasts help 
            businesses make informed inventory and marketing decisions.""",
            verbose=True,
            allow_delegation=False
        )
    
    def _create_risk_agent(self):
        """Create the risk assessment agent."""
        return Agent(
            role="Risk Analyst",
            goal="Identify potential risks and opportunities in sales forecasts",
            backstory="""You are a seasoned risk analyst who specializes in identifying 
            potential stockouts, inventory issues, and market opportunities based on 
            sales trends and forecasts.""",
            verbose=True,
            allow_delegation=False
        )
    
    def _create_narrative_agent(self):
        """Create the narrative agent."""
        return Agent(
            role="Narrative Analyst",
            goal="Create clear, actionable insights from forecasts and risk assessments",
            backstory="""You are a skilled communicator who translates complex data 
            into clear, actionable narratives for business stakeholders. Your insights 
            guide strategic decisions across product and marketing teams.""",
            verbose=True,
            allow_delegation=False
        )
    
    def process_data(self, data_path: str, forecast_months: int = 1, use_llm: bool = False) -> AgentResponse:
        """
        Process sales data and generate forecasts.
        
        Args:
            data_path: Path to the CSV data file
            forecast_months: Number of months to forecast (1-3)
            use_llm: Whether to use LLM-based forecasting
            
        Returns:
            AgentResponse object with forecasts and summary
        """
        # Validate forecast months (between 1 and 3)
        forecast_months = max(1, min(3, forecast_months))
        
        # Load data
        df = pd.read_csv(data_path)
        
        # Extract sales history
        sales_cols = [col for col in df.columns if col.startswith('sales_m')]
        
        # Set up tasks
        forecast_task = self._create_forecast_task(df, sales_cols, forecast_months, use_llm)
        risk_task = self._create_risk_task()
        narrative_task = self._create_narrative_task()
        
        # Create and run crew
        crew = Crew(
            agents=[self.forecaster_agent, self.risk_agent, self.narrative_agent],
            tasks=[forecast_task, risk_task, narrative_task],
            process=Process.sequential
        )
        
        # Since we're simulating the CrewAI execution, we'll directly call our methods
        # Process the data
        forecasts = self._generate_forecasts(df, sales_cols, forecast_months, use_llm)
        forecasts = self._add_risk_indicators(forecasts)
        forecasts = self._add_narratives(forecasts)
        
        # Create summary
        summary = self._generate_summary(forecasts)
        
        # Return response
        return AgentResponse(
            forecasts=forecasts,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_forecast_task(self, df, sales_cols, forecast_months, use_llm):
        """Create the forecasting task."""
        method = "LLM-based" if use_llm else "statistical"
        return Task(
            description=f"Generate {method} sales forecasts for {forecast_months} month(s) ahead",
            agent=self.forecaster_agent,
            expected_output="Sales forecasts with confidence scores"
        )
    
    def _create_risk_task(self):
        """Create the risk assessment task."""
        return Task(
            description="Analyze forecasts to identify potential risks and opportunities",
            agent=self.risk_agent,
            expected_output="Risk indicators for each product"
        )
    
    def _create_narrative_task(self):
        """Create the narrative generation task."""
        return Task(
            description="Create clear, actionable narratives based on forecasts and risk assessments",
            agent=self.narrative_agent,
            expected_output="Concise narrative insights for each product"
        )
    
    def _generate_forecasts(self, df: pd.DataFrame, sales_cols: List[str], forecast_months: int, use_llm: bool = False) -> List[ForecastResult]:
        """Generate forecasts for each product."""
        forecasts = []
        
        # Validate forecast_months is between 1 and 3
        forecast_months = max(1, min(3, forecast_months))
        
        for _, row in df.iterrows():
            # Extract sales history
            sales_history = [row[col] for col in sales_cols]
            
            if use_llm:
                # Import the LLM forecaster only when needed
                global llm_forecaster
                if llm_forecaster is None:
                    import llm_forecaster
                # Use LLM-based forecasting
                llm_result = llm_forecaster.generate_llm_forecast(
                    product_name=row['product_name'],
                    category=row['category'],
                    sales_history=sales_history,
                    forecast_months=forecast_months
                )
                
                # Create a forecast result for each month
                for month_idx, month_data in enumerate(llm_result['forecasts']):
                    # Make sure data fields exist with proper fallbacks
                    forecast_value = month_data.get('forecast_value', month_data.get('value', 0))
                    confidence = month_data.get('confidence', 0.75)
                    
                    # Create forecast result
                    forecast = ForecastResult(
                        product_id=row['product_id'],
                        product_name=row['product_name'],
                        category=row['category'],
                        forecast_value=round(float(forecast_value), 2),
                        confidence_score=float(confidence),
                        trend_tag=llm_result['trend_tag'],
                        risk_indicator="",  # Will be filled by risk agent
                        narrative="",       # Will be filled by narrative agent
                        forecast_months=month_idx + 1
                    )
                    
                    forecasts.append(forecast)
            else:
                # Use statistical forecasting
                # Generate forecast for each requested future month
                for month_idx in range(forecast_months):
                    # Calculate forecast for this month
                    forecast_values = utils.calculate_statistical_forecast(sales_history, periods=forecast_months)
                    forecast_value = forecast_values[month_idx]
                    
                    # Calculate confidence score
                    confidence = utils.calculate_confidence_score(sales_history)
                    
                    # Determine trend tag
                    trend_tag = utils.determine_trend_tag(sales_history, forecast_value)
                    
                    # Create forecast result
                    forecast = ForecastResult(
                        product_id=row['product_id'],
                        product_name=row['product_name'],
                        category=row['category'],
                        forecast_value=round(forecast_value, 2),
                        confidence_score=confidence,
                        trend_tag=trend_tag,
                        risk_indicator="",  # Will be filled by risk agent
                        narrative="",       # Will be filled by narrative agent
                        forecast_months=month_idx + 1
                    )
                    
                    forecasts.append(forecast)
                    
                    # For multi-month forecasts, add the forecast to history for next prediction
                    if month_idx < forecast_months - 1:
                        sales_history.append(forecast_value)
        
        return forecasts
    
    def _add_risk_indicators(self, forecasts: List[ForecastResult]) -> List[ForecastResult]:
        """Add risk indicators to forecasts."""
        for forecast in forecasts:
            # In a real implementation, this would be part of the risk agent's task
            # Here we're simulating its output
            risk_indicator = utils.determine_risk_indicator(
                sales_history=[],  # We don't have the history here, would be passed in real implementation
                forecast=forecast.forecast_value,
                trend_score=0.5    # Using a default value
            )
            
            # Override with more specific indicators based on product trends
            if forecast.trend_tag == "rising" and forecast.confidence_score > 0.7:
                risk_indicator = "possible stockout"
            elif forecast.trend_tag == "declining" and forecast.confidence_score > 0.6:
                risk_indicator = "possible excess inventory"
            elif forecast.trend_tag == "volatile":
                risk_indicator = "demand volatility risk"
            elif forecast.trend_tag == "flat" and forecast.confidence_score > 0.8:
                risk_indicator = "stable demand"
            elif forecast.trend_tag == "stable" and forecast.confidence_score > 0.8:
                risk_indicator = "stable demand"
            
            forecast.risk_indicator = risk_indicator
        
        return forecasts
    
    def _add_narratives(self, forecasts: List[ForecastResult]) -> List[ForecastResult]:
        """Add narrative insights to forecasts."""
        for forecast in forecasts:
            # In a real implementation, this would be part of the narrative agent's task
            # Here we're simulating its output
            
            if forecast.risk_indicator == "possible stockout":
                narrative = f"{forecast.product_name} is showing strong upward momentum - expect higher sales next month. Consider increasing inventory levels to prevent stockouts."
            
            elif forecast.risk_indicator == "possible excess inventory":
                narrative = f"{forecast.product_name} is expected to underperform next month. Consider promotions to reduce inventory or adjust purchasing plans."
            
            elif forecast.risk_indicator == "demand volatility risk":
                narrative = f"{forecast.product_name} shows unpredictable demand patterns. Consider more frequent inventory reviews and flexible supply arrangements."
            
            elif forecast.risk_indicator == "stable demand":
                narrative = f"{forecast.product_name} shows steady, predictable demand. Maintain current inventory levels and standard reordering processes."
            
            else:
                narrative = f"{forecast.product_name} forecasted sales are in line with recent performance. No significant changes to inventory management needed."
            
            forecast.narrative = narrative
        
        return forecasts
    
    def _generate_summary(self, forecasts: List[ForecastResult]) -> str:
        """Generate a summary of all forecasts."""
        total_products = len(set(f.product_id for f in forecasts))
        max_forecast_months = max([f.forecast_months for f in forecasts]) if forecasts else 0
        rising_products = len([f for f in forecasts if f.trend_tag == "rising"])
        declining_products = len([f for f in forecasts if f.trend_tag == "declining"])
        volatile_products = len([f for f in forecasts if f.trend_tag == "volatile"])
        stable_products = len([f for f in forecasts if f.trend_tag == "stable" or f.trend_tag == "flat"])
        stockout_risks = len([f for f in forecasts if "stockout" in f.risk_indicator])
        excess_inventory_risks = len([f for f in forecasts if "excess inventory" in f.risk_indicator])
        
        summary = f"""
        Forecast Summary:
        - Analyzed {total_products} products for {max_forecast_months} month{'s' if max_forecast_months > 1 else ''} ahead
        - {rising_products} products show rising trends
        - {declining_products} products show declining trends
        - {volatile_products} products show volatile patterns
        - {stable_products} products show stable/flat trends
        - {stockout_risks} products at risk of stockout
        - {excess_inventory_risks} products at risk of excess inventory

        Key actions to consider:
        - Update inventory levels for products with stockout risks
        - Review marketing for declining products
        - Prepare visual assets for seasonal trending products
        - Monitor volatile products more frequently
        """
        
        return summary
