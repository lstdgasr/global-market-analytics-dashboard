from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MACRO_PATH = PROJECT_ROOT / "data" / "sample" / "macro_indicators.csv"
LIVE_MACRO_PATH = PROJECT_ROOT / "data" / "live" / "macro_indicators.csv"

WORLD_BANK_API = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

MARKET_COUNTRY_MAP = {
    "S&P 500": "USA",
    "NASDAQ Composite": "USA",
    "FTSE 100": "GBR",
    "Nikkei 225": "JPN",
    "Hang Seng Index": "HKG",
}

COUNTRIES = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "JPN": "Japan",
    "HKG": "Hong Kong SAR, China",
    "CHN": "China",
}

MACRO_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": {
        "indicator_name": "GDP growth",
        "unit": "annual %",
        "category": "growth",
    },
    "FP.CPI.TOTL.ZG": {
        "indicator_name": "Inflation",
        "unit": "annual %",
        "category": "price",
    },
    "SL.UEM.TOTL.ZS": {
        "indicator_name": "Unemployment",
        "unit": "% of labor force",
        "category": "labor",
    },
    "CM.MKT.LCAP.GD.ZS": {
        "indicator_name": "Market capitalization to GDP",
        "unit": "% of GDP",
        "category": "market_depth",
    },
}

REQUIRED_MACRO_COLUMNS = {
    "country_code",
    "country_name",
    "year",
    "indicator_code",
    "indicator_name",
    "value",
    "unit",
    "category",
}


@dataclass(frozen=True)
class MacroDataSource:
    path: Path
    label: str


def resolve_macro_source(prefer_live: bool = True) -> MacroDataSource:
    if prefer_live and LIVE_MACRO_PATH.exists():
        return MacroDataSource(LIVE_MACRO_PATH, "Live macro dataset / 在线宏观数据")
    return MacroDataSource(SAMPLE_MACRO_PATH, "Sample macro dataset / 样例宏观数据")


def parse_world_bank_records(payload: Any, indicator_code: str) -> pd.DataFrame:
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return _empty_macro_frame()

    metadata = MACRO_INDICATORS[indicator_code]
    records = []
    for item in payload[1]:
        value = item.get("value")
        if value is None:
            continue

        records.append(
            {
                "country_code": item.get("countryiso3code"),
                "country_name": item.get("country", {}).get("value"),
                "year": int(item.get("date")),
                "indicator_code": indicator_code,
                "indicator_name": metadata["indicator_name"],
                "value": float(value),
                "unit": metadata["unit"],
                "category": metadata["category"],
            }
        )

    if not records:
        return _empty_macro_frame()

    return pd.DataFrame.from_records(records).sort_values(["country_code", "indicator_code", "year"])


def download_world_bank_indicator(
    indicator_code: str,
    countries: list[str] | None = None,
    start_year: int = 2020,
    end_year: int = 2024,
    timeout: int = 30,
) -> pd.DataFrame:
    if indicator_code not in MACRO_INDICATORS:
        raise ValueError(f"Unsupported World Bank indicator: {indicator_code}")

    country_codes = countries or list(COUNTRIES)
    url = WORLD_BANK_API.format(
        countries=";".join(country_codes),
        indicator=indicator_code,
    )
    response = requests.get(
        url,
        params={
            "format": "json",
            "date": f"{start_year}:{end_year}",
            "per_page": 500,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return parse_world_bank_records(response.json(), indicator_code)


def download_macro_data(start_year: int = 2020, end_year: int = 2024) -> pd.DataFrame:
    frames = [
        download_world_bank_indicator(
            indicator_code,
            start_year=start_year,
            end_year=end_year,
        )
        for indicator_code in MACRO_INDICATORS
    ]
    data = pd.concat(frames, ignore_index=True)
    return clean_macro_data(data)


def load_macro_data(path: Path | str | None = None, prefer_live: bool = True) -> pd.DataFrame:
    source_path = Path(path) if path is not None else resolve_macro_source(prefer_live).path
    if not source_path.exists():
        raise FileNotFoundError(f"Macro data file not found: {source_path}")

    data = pd.read_csv(source_path)
    return clean_macro_data(data)


def clean_macro_data(data: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_MACRO_COLUMNS.difference(data.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required macro columns: {missing_text}")

    cleaned = data.copy()
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce").astype("Int64")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = cleaned.dropna(subset=["country_code", "year", "indicator_code", "value"])
    cleaned["year"] = cleaned["year"].astype(int)
    return cleaned.sort_values(["country_code", "indicator_code", "year"]).reset_index(drop=True)


def latest_macro_snapshot(macro_data: pd.DataFrame) -> pd.DataFrame:
    if macro_data.empty:
        return _empty_macro_frame()

    sorted_data = macro_data.sort_values(["country_code", "indicator_code", "year"])
    latest = sorted_data.groupby(["country_code", "indicator_code"], as_index=False).tail(1)
    return latest.reset_index(drop=True)


def macro_pivot(macro_data: pd.DataFrame) -> pd.DataFrame:
    if macro_data.empty:
        return pd.DataFrame()

    latest = latest_macro_snapshot(macro_data)
    pivot = latest.pivot_table(
        index=["country_code", "country_name"],
        columns="indicator_name",
        values="value",
        aggfunc="last",
    )
    return pivot.reset_index().rename_axis(None, axis=1)


def attach_macro_to_summary(summary: pd.DataFrame, macro_data: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary.copy()

    enriched = summary.copy().reset_index(names="index_name")
    enriched["country_code"] = enriched["index_name"].map(MARKET_COUNTRY_MAP)
    macro = macro_pivot(macro_data)
    return enriched.merge(macro, on="country_code", how="left")


def save_macro_data(macro_data: pd.DataFrame, path: Path | str = LIVE_MACRO_PATH) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    clean_macro_data(macro_data).to_csv(target, index=False)
    return target


def _empty_macro_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=sorted(REQUIRED_MACRO_COLUMNS))

