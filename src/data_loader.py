from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "index_prices.csv"
LIVE_DATA_PATH = PROJECT_ROOT / "data" / "live" / "index_prices.csv"

REQUIRED_COLUMNS = {"date", "index_name", "ticker", "region", "currency", "close"}

DEFAULT_MARKETS = {
    "^GSPC": {"index_name": "S&P 500", "region": "United States", "currency": "USD"},
    "^IXIC": {"index_name": "NASDAQ Composite", "region": "United States", "currency": "USD"},
    "^FTSE": {"index_name": "FTSE 100", "region": "United Kingdom", "currency": "GBP"},
    "^N225": {"index_name": "Nikkei 225", "region": "Japan", "currency": "JPY"},
    "^HSI": {"index_name": "Hang Seng Index", "region": "Hong Kong", "currency": "HKD"},
}


@dataclass(frozen=True)
class DataSource:
    """A resolved data source for display in the dashboard."""

    path: Path
    label: str


def resolve_data_source(prefer_live: bool = True) -> DataSource:
    if prefer_live and LIVE_DATA_PATH.exists():
        return DataSource(LIVE_DATA_PATH, "Live dataset / 在线数据")
    return DataSource(SAMPLE_DATA_PATH, "Sample dataset / 样例数据")


def load_index_prices(path: Path | str | None = None, prefer_live: bool = True) -> pd.DataFrame:
    source_path = Path(path) if path is not None else resolve_data_source(prefer_live).path
    if not source_path.exists():
        raise FileNotFoundError(f"Data file not found: {source_path}")

    data = pd.read_csv(source_path)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_text}")

    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna(subset=["date", "index_name", "close"])
    data = data.sort_values(["index_name", "date"]).reset_index(drop=True)
    return data


def filter_prices(
    prices: pd.DataFrame,
    markets: list[str] | None = None,
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    filtered = prices.copy()
    if markets:
        filtered = filtered[filtered["index_name"].isin(markets)]
    if start_date is not None:
        filtered = filtered[filtered["date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["date"] <= pd.Timestamp(end_date)]
    return filtered.reset_index(drop=True)


def price_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty:
        return pd.DataFrame()
    matrix = prices.pivot_table(
        index="date",
        columns="index_name",
        values="close",
        aggfunc="last",
    )
    return matrix.sort_index().ffill()


def close_series_from_history(history: pd.DataFrame, ticker: str) -> pd.Series:
    if "Adj Close" in history.columns:
        close = history["Adj Close"]
    elif "Close" in history.columns:
        close = history["Close"]
    else:
        raise ValueError(f"No close price column returned for {ticker}")

    if isinstance(close, pd.DataFrame):
        if ticker in close.columns:
            close = close[ticker]
        else:
            close = close.iloc[:, 0]

    return pd.to_numeric(close, errors="coerce").dropna()


def download_market_data(
    start: str,
    end: str | None = None,
    markets: dict[str, dict[str, str]] | None = None,
) -> pd.DataFrame:
    import yfinance as yf

    market_map = markets or DEFAULT_MARKETS
    frames: list[pd.DataFrame] = []

    for ticker, metadata in market_map.items():
        history = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            actions=False,
        )
        if history.empty:
            continue

        close = close_series_from_history(history, ticker)
        if close.empty:
            continue

        frame = pd.DataFrame(
            {
                "date": close.index,
                "index_name": metadata["index_name"],
                "ticker": ticker,
                "region": metadata["region"],
                "currency": metadata["currency"],
                "close": close.to_numpy(dtype=float),
            }
        )
        frames.append(frame)

    if not frames:
        raise RuntimeError("No market data was returned by the online data provider.")

    data = pd.concat(frames, ignore_index=True)
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    return data.sort_values(["index_name", "date"]).reset_index(drop=True)


def save_prices(prices: pd.DataFrame, path: Path | str = LIVE_DATA_PATH) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(target, index=False)
    return target
