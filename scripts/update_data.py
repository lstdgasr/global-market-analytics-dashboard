from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import LIVE_DATA_PATH, download_market_data, save_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update global equity index data from Yahoo Finance.")
    parser.add_argument("--start", default="2021-01-01", help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end", default=None, help="Optional end date in YYYY-MM-DD format.")
    parser.add_argument("--output", default=str(LIVE_DATA_PATH), help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end = args.end or date.today().isoformat()
    prices = download_market_data(start=args.start, end=end)
    path = save_prices(prices, args.output)
    print(f"Saved {len(prices):,} rows to {path}")


if __name__ == "__main__":
    main()
