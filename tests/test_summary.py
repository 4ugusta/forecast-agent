"""The forecast summary counts each product once, at its nearest month."""

from forecast_agent import ForecastAgentSystem
from models import ForecastResult


def result(pid, month, trend, risk):
    return ForecastResult(product_id=pid, product_name=f"P{pid}", category="C", forecast_value=10.0,
                          confidence_score=0.9, trend_tag=trend, risk_indicator=risk, narrative="n",
                          forecast_months=month)


def test_two_products_over_two_months_count_once_each_from_their_nearest_month():
    # given out of order; month 2 disagrees with month 1 on purpose
    forecasts = [
        result(1, 2, "flat", "unknown"),
        result(2, 1, "rising", "possible stockout"),
        result(1, 1, "declining", "possible excess inventory"),
        result(2, 2, "volatile", "unknown"),
    ]
    summary = ForecastAgentSystem._generate_summary(None, forecasts)
    assert "Analyzed 2 products for 2 months ahead" in summary
    assert "1 products show rising trends" in summary
    assert "1 products show declining trends" in summary
    assert "0 products show volatile patterns" in summary
    assert "0 products show stable/flat trends" in summary
    assert "1 products at risk of stockout" in summary
    assert "1 products at risk of excess inventory" in summary
