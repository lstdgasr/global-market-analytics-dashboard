from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.macro_loader import LIVE_MACRO_PATH, download_macro_data, save_macro_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update macro indicators from the World Bank API.")
    parser.add_argument("--start-year", type=int, default=2020, help="First year to download.")
    parser.add_argument("--end-year", type=int, default=2024, help="Last year to download.")
    parser.add_argument("--output", default=str(LIVE_MACRO_PATH), help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = download_macro_data(start_year=args.start_year, end_year=args.end_year)
    path = save_macro_data(data, args.output)
    print(f"Saved {len(data):,} macro rows to {path}")


if __name__ == "__main__":
    main()

