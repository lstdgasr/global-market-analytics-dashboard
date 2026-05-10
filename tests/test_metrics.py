import pandas as pd
import pytest

from src.metrics import (
    annualized_volatility,
    correlation_matrix,
    cumulative_returns,
    max_drawdowns,
    normalized_prices,
    risk_return_summary,
)


def test_cumulative_returns_are_sorted_descending():
    prices = pd.DataFrame(
        {
            "Market A": [100.0, 110.0, 121.0],
            "Market B": [100.0, 90.0, 95.0],
        },
        index=pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31"]),
    )

    result = cumulative_returns(prices)

    assert list(result.index) == ["Market A", "Market B"]
    assert result["Market A"] == pytest.approx(0.21)
    assert result["Market B"] == pytest.approx(-0.05)


def test_annualized_volatility_handles_constant_prices():
    prices = pd.DataFrame(
        {"Stable Market": [100.0, 100.0, 100.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31"]),
    )

    result = annualized_volatility(prices)

    assert result["Stable Market"] == 0.0


def test_max_drawdown_identifies_deepest_decline():
    prices = pd.DataFrame(
        {"Market A": [100.0, 120.0, 90.0, 105.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30"]),
    )

    result = max_drawdowns(prices)

    assert result["Market A"] == pytest.approx(-0.25)


def test_correlation_matrix_uses_returns_not_price_levels():
    prices = pd.DataFrame(
        {
            "Market A": [100.0, 110.0, 99.0, 108.9],
            "Market B": [200.0, 220.0, 198.0, 217.8],
        },
        index=pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30"]),
    )

    result = correlation_matrix(prices)

    assert result.loc["Market A", "Market B"] == pytest.approx(1.0)


def test_normalized_prices_start_at_base_value():
    prices = pd.DataFrame(
        {"Market A": [50.0, 55.0], "Market B": [200.0, 220.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29"]),
    )

    result = normalized_prices(prices)

    assert result.iloc[0]["Market A"] == pytest.approx(100.0)
    assert result.iloc[1]["Market B"] == pytest.approx(110.0)


def test_risk_return_summary_contains_expected_columns():
    prices = pd.DataFrame(
        {"Market A": [100.0, 110.0, 115.0], "Market B": [100.0, 95.0, 90.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31"]),
    )

    result = risk_return_summary(prices)

    assert set(result.columns) == {
        "cumulative_return",
        "annualized_volatility",
        "max_drawdown",
        "return_to_risk",
    }
    assert result.index[0] == "Market A"

