"""
Main script to run the Forecast Agent.
"""

import os
import json
import argparse
import sys
import uvicorn
from pathlib import Path

from forecast_agent import ForecastAgentSystem
from cli_api import app as api_app


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fegmo Forecast Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run the CLI tool")
    cli_parser.add_argument("--data", "-d", required=True, help="Path to CSV data file")
    cli_parser.add_argument("--months", "-m", type=int, default=1, choices=[1, 2, 3], help="Number of months to forecast (1-3)")
    cli_parser.add_argument("--llm", action="store_true", help="Use LLM-based forecasting (requires OPENAI_API_KEY)")
    cli_parser.add_argument("--output", "-o", help="Output JSON file path")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", default="127.0.0.1", help="Host to listen on")
    api_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on")
    
    # Sample command
    sample_parser = subparsers.add_parser("sample", help="Run with sample data")
    sample_parser.add_argument("--months", "-m", type=int, default=1, choices=[1, 2, 3], help="Number of months to forecast (1-3)")
    sample_parser.add_argument("--llm", action="store_true", help="Use LLM-based forecasting (requires OPENAI_API_KEY)")
    
    args = parser.parse_args()
    
    if args.command == "cli":
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
    
    elif args.command == "api":
        print(f"Starting API server at http://{args.host}:{args.port}")
        uvicorn.run(api_app, host=args.host, port=args.port)
    
    elif args.command == "sample":
        # Use the sample data included with the package
        sample_path = Path(__file__).parent / "sample_data.csv"
        if not sample_path.exists():
            print(f"Error: Sample data file not found at '{sample_path}'")
            sys.exit(1)
        
        print(f"Processing sample data...")
        agent_system = ForecastAgentSystem()
        response = agent_system.process_data(
            data_path=str(sample_path),
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
        print(json.dumps(result, indent=4))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
