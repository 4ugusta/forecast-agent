# Fegmo Forecast Agent

A lightweight, agentic forecasting system for e-commerce sales prediction.

## Overview

The Forecast Agent analyzes historical sales data to:

1. Predict future sales for each product
2. Identify potential risks (stockouts, excess inventory)
3. Generate narrative insights for business actions

This system uses a multi-agent approach with:
- **Forecaster Agent**: Builds and runs forecasting models
- **Risk Agent**: Identifies business risks and opportunities
- **Narrative Agent**: Translates data into actionable insights

## Features

- Statistical forecasting for 1-3 months ahead
- LLM-based forecasting using OpenAI (optional)
- Confidence scoring for each prediction
- Trend tagging (rising, declining, volatile, flat, stable)
- Risk indicators for inventory management
- Narrative insights per product
- Both CLI and API interfaces

## System Requirements

- Python 3.12 or later
- macOS, Linux, or Windows
- OpenAI API key (for LLM-based forecasting)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd forecast-agent

# Set up the environment (requires Python 3.12+)
bash setup_python312.sh

# Set up OpenAI API key for LLM-based forecasting
python setup_openai.py
```

## Usage

### Sample Data

To quickly test with the included sample data:

```bash
# Statistical forecasting
python main.py sample --months 1

# LLM-based forecasting
python main.py sample --months 2 --llm
```

### CLI

Process your own data file:

```bash
python main.py cli --data your_data.csv --months 3 --output results.json
```

Options:
- `--data` / `-d`: Path to CSV data file
- `--months` / `-m`: Number of months to forecast (1-3)
- `--llm`: Use LLM-based forecasting (optional)
- `--output` / `-o`: Output JSON file path (optional)

### API

Start the API server:

```bash
python main.py api --port 8000
```

Then send a POST request to `/forecast` with:
- A CSV file upload
- Optional form parameters:
  - `forecast_months`: Number of months to forecast
  - `use_llm`: Whether to use LLM-based forecasting

Example using curl:

```bash
curl -X POST \
  -F "file=@sample_data.csv" \
  -F "forecast_months=2" \
  http://localhost:8000/forecast
```

## Data Format

The CSV file should have the following columns:

```
product_id,product_name,category,sales_m1,sales_m2,sales_m3,sales_m4,sales_m5,sales_m6,trend_score
```

Where:
- `product_id`: Unique identifier for the product
- `product_name`: Name of the product
- `category`: Product category
- `sales_m1` to `sales_m6`: Historical monthly sales (oldest to newest)
- `trend_score`: Optional pre-calculated trend score (0-1)

## Output Format

The system returns a JSON object with:

```json
{
  "forecasts": [
    {
      "product_id": 101,
      "product_name": "Herbal Shampoo",
      "category": "Haircare",
      "forecast_value": 220.45,
      "confidence_score": 0.85,
      "trend_tag": "rising",
      "risk_indicator": "possible stockout",
      "narrative": "Herbal Shampoo is showing strong upward momentum - expect higher sales next month. Consider increasing inventory levels to prevent stockouts.",
      "forecast_months": 1
    },
    // ... more products
  ],
  "summary": "Forecast Summary:\n- Analyzed 10 products\n- 4 products show rising trends\n- 2 products show declining trends\n- 2 products at risk of stockout",
  "timestamp": "2025-06-16T12:34:56.789Z"
}
```

## Integration with Fegmo Platform

This forecast agent is designed to integrate with Fegmo's agentic PIM and DAM platform by:

1. Triggering urgency messages for products at risk of stockout
2. Scheduling seasonal assets for trending products
3. Alerting the Readiness Agent about demand changes
4. Providing insights for inventory and marketing decisions
