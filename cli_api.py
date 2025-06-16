"""
CLI and API interfaces for the Forecast Agent.
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel

from forecast_agent import ForecastAgentSystem
from models import AgentResponse, ForecastResult


# Initialize FastAPI
app = FastAPI(
    title="Forecast Agent API",
    description="API for the agentic forecasting system",
    version="0.1.0"
)


class ForecastRequest(BaseModel):
    """Request model for forecast endpoint."""
    forecast_months: int = 1
    use_llm: bool = False


class ForecastResponse(BaseModel):
    """Response model for forecast endpoint."""
    forecasts: List[dict]
    summary: str
    timestamp: str


@app.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(
    file: UploadFile = File(...),
    forecast_months: int = Form(1),
    use_llm: bool = Form(False)
):
    """
    Generate forecast from uploaded CSV file.
    
    Args:
        file: CSV file with sales data
        forecast_months: Number of months to forecast (1-3)
        use_llm: Whether to use LLM-based forecasting
        
    Returns:
        Forecast results and summary
    """
    # Validate forecast_months is between 1 and 3
    forecast_months = max(1, min(3, forecast_months))
    # Save uploaded file
    temp_file = Path(f"/tmp/forecast_data_{datetime.now().timestamp()}.csv")
    with open(temp_file, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Process data
    agent_system = ForecastAgentSystem()
    response = agent_system.process_data(
        data_path=str(temp_file),
        forecast_months=forecast_months,
        use_llm=use_llm
    )
    
    # Convert to dict for response
    return {
        "forecasts": [forecast.model_dump() for forecast in response.forecasts],
        "summary": response.summary,
        "timestamp": response.timestamp
    }


def run_cli():
    """Run the CLI interface."""
    parser = argparse.ArgumentParser(description="Forecast Agent CLI")
    parser.add_argument("--data", "-d", required=True, help="Path to CSV data file")
    parser.add_argument("--months", "-m", type=int, default=1, choices=[1, 2, 3], help="Number of months to forecast (1-3)")
    parser.add_argument("--llm", action="store_true", help="Use LLM-based forecasting (requires OPENAI_API_KEY)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.data).exists():
        print(f"Error: Data file '{args.data}' does not exist.")
        sys.exit(1)
    
    # Process data
    print(f"Processing data from '{args.data}'...")
    agent_system = ForecastAgentSystem()
    response = agent_system.process_data(
        data_path=args.data,
        forecast_months=args.months,
        use_llm=args.llm
    )
    
    # Convert to JSON
    result = {
        "forecasts": [forecast.model_dump() for forecast in response.forecasts],
        "summary": response.summary,
        "timestamp": response.timestamp
    }
    
    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=4)
        print(f"Results saved to '{args.output}'")
    else:
        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    run_cli()
