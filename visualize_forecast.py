"""
Visualization tools for the forecast results.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, List, Any

def load_forecast_results(json_data: Dict[str, Any]) -> pd.DataFrame:
    """Load forecast results from a JSON object."""
    forecasts = json_data["forecasts"]
    df = pd.DataFrame(forecasts)
    return df

def plot_forecasts(df: pd.DataFrame, sample_data_path: str):
    """Create visualizations of the forecast results."""
    # One row per product, its nearest month: a multi-month run has a row per month, which drew
    # "Top 5 Products" as three bars and counted twice as many trend tags as products
    df = df.sort_values("forecast_months").drop_duplicates("product_id")

    # Load sample data to get historical values
    sample_df = pd.read_csv(sample_data_path)
    
    # Set up the plot style
    sns.set(style="whitegrid")
    
    # Create figure and subplots
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Top Products by Forecast Value
    plt.subplot(2, 2, 1)
    top_products = df.sort_values(by="forecast_value", ascending=False).head(5)
    sns.barplot(x="forecast_value", y="product_name", data=top_products)
    plt.title("Top 5 Products by Forecast Value")
    plt.xlabel("Forecast Value")
    plt.tight_layout()
    
    # 2. Confidence Score Distribution
    plt.subplot(2, 2, 2)
    sns.histplot(df["confidence_score"], bins=10, kde=True)
    plt.title("Confidence Score Distribution")
    plt.xlabel("Confidence Score")
    plt.tight_layout()
    
    # 3. Trend Tag Distribution
    plt.subplot(2, 2, 3)
    trend_counts = df["trend_tag"].value_counts()
    sns.barplot(x=trend_counts.index, y=trend_counts.values)
    plt.title("Trend Tag Distribution")
    plt.ylabel("Count")
    plt.tight_layout()
    
    # 4. Historical vs Forecast for a sample product
    plt.subplot(2, 2, 4)
    
    # Try to get a product with an interesting trend for demonstration
    # First look for rising, then declining, then any product if those don't exist
    if not df[df["trend_tag"] == "rising"].empty:
        product_id = df[df["trend_tag"] == "rising"].iloc[0]["product_id"]
    elif not df[df["trend_tag"] == "declining"].empty:
        product_id = df[df["trend_tag"] == "declining"].iloc[0]["product_id"]
    else:
        product_id = df.iloc[0]["product_id"]
        
    product_row = sample_df[sample_df["product_id"] == product_id].iloc[0]
    product_name = product_row["product_name"]
    
    # Get historical data
    hist_data = [
        product_row["sales_m1"],
        product_row["sales_m2"],
        product_row["sales_m3"],
        product_row["sales_m4"],
        product_row["sales_m5"],
        product_row["sales_m6"]
    ]
    
    # Get forecast value
    forecast_value = df[df["product_id"] == product_id].iloc[0]["forecast_value"]
    
    # Create x-axis labels
    months = [f"M{i}" for i in range(1, 7)] + ["Forecast"]
    
    # Plot
    plt.plot(months[:-1], hist_data, marker='o', linestyle='-', color='blue', label='Historical')
    plt.plot(months[-2:], [hist_data[-1], forecast_value], marker='o', linestyle='--', color='red', label='Forecast')
    plt.title(f"Historical vs Forecast: {product_name}")
    plt.xlabel("Month")
    plt.ylabel("Sales")
    plt.legend()
    plt.tight_layout()
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig("forecast_visualization.png")
    
    print(f"Visualization saved as 'forecast_visualization.png'")
    return fig

def main():
    """Run the visualization."""
    import argparse
    import sys
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Forecast Visualization Tool")
    parser.add_argument("--result", "-r", required=True, help="Path to JSON results file")
    parser.add_argument("--data", "-d", default="sample_data.csv", help="Path to original CSV data file")
    
    args = parser.parse_args()
    
    # Check if files exist
    result_path = args.result
    data_path = args.data
    
    if not Path(result_path).exists():
        print(f"Error: Results file '{result_path}' does not exist.")
        sys.exit(1)
    
    if not Path(data_path).exists():
        print(f"Error: Data file '{data_path}' does not exist.")
        sys.exit(1)
    
    # Load results
    with open(result_path, 'r') as f:
        results = json.load(f)
    
    # Create visualization
    df = load_forecast_results(results)
    plot_forecasts(df, data_path)

if __name__ == "__main__":
    main()
