import pandas as pd
import pytest

from src.macro_loader import (
    MARKET_COUNTRY_MAP,
    attach_macro_to_summary,
    latest_macro_snapshot,
    parse_world_bank_records,
)


def test_parse_world_bank_records_skips_null_values():
    payload = [
        {"page": 1},
        [
            {
                "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"},
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2024",
                "value": 2.8,
            },
            {
                "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"},
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2023",
                "value": None,
            },
        ],
    ]

    result = parse_world_bank_records(payload, "NY.GDP.MKTP.KD.ZG")

    assert len(result) == 1
    assert result.iloc[0]["country_code"] == "USA"
    assert result.iloc[0]["value"] == pytest.approx(2.8)


def test_latest_macro_snapshot_uses_latest_available_year_per_indicator():
    macro = pd.DataFrame(
        {
            "country_code": ["USA", "USA", "USA"],
            "country_name": ["United States", "United States", "United States"],
            "year": [2021, 2022, 2024],
            "indicator_code": ["CM.MKT.LCAP.GD.ZS", "CM.MKT.LCAP.GD.ZS", "NY.GDP.MKTP.KD.ZG"],
            "indicator_name": ["Market capitalization to GDP", "Market capitalization to GDP", "GDP growth"],
            "value": [208.2, 157.4, 2.8],
            "unit": ["% of GDP", "% of GDP", "annual %"],
            "category": ["market_depth", "market_depth", "growth"],
        }
    )

    result = latest_macro_snapshot(macro)

    market_depth = result[result["indicator_code"] == "CM.MKT.LCAP.GD.ZS"].iloc[0]
    assert market_depth["year"] == 2022
    assert market_depth["value"] == pytest.approx(157.4)


def test_market_country_mapping_covers_current_dashboard_markets():
    assert MARKET_COUNTRY_MAP["S&P 500"] == "USA"
    assert MARKET_COUNTRY_MAP["NASDAQ Composite"] == "USA"
    assert MARKET_COUNTRY_MAP["FTSE 100"] == "GBR"
    assert MARKET_COUNTRY_MAP["Nikkei 225"] == "JPN"
    assert MARKET_COUNTRY_MAP["Hang Seng Index"] == "HKG"


def test_attach_macro_to_summary_adds_country_indicators():
    summary = pd.DataFrame(
        {
            "cumulative_return": {"S&P 500": 0.2},
            "annualized_volatility": {"S&P 500": 0.1},
            "max_drawdown": {"S&P 500": -0.1},
            "return_to_risk": {"S&P 500": 2.0},
        }
    )
    macro = pd.DataFrame(
        {
            "country_code": ["USA"],
            "country_name": ["United States"],
            "year": [2024],
            "indicator_code": ["NY.GDP.MKTP.KD.ZG"],
            "indicator_name": ["GDP growth"],
            "value": [2.8],
            "unit": ["annual %"],
            "category": ["growth"],
        }
    )

    result = attach_macro_to_summary(summary, macro)

    assert result.iloc[0]["country_code"] == "USA"
    assert result.iloc[0]["GDP growth"] == pytest.approx(2.8)

