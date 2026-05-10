import pandas as pd
import pytest

from src.data_loader import close_series_from_history


def test_close_series_from_history_handles_multiindex_yfinance_output():
    columns = pd.MultiIndex.from_tuples(
        [("Adj Close", "^GSPC"), ("Close", "^GSPC")],
        names=["Price", "Ticker"],
    )
    history = pd.DataFrame(
        [[101.0, 100.0], [102.5, 102.0]],
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
        columns=columns,
    )

    result = close_series_from_history(history, "^GSPC")

    assert result.tolist() == [101.0, 102.5]


def test_close_series_from_history_raises_when_close_is_missing():
    history = pd.DataFrame({"Open": [100.0]}, index=pd.to_datetime(["2024-01-02"]))

    with pytest.raises(ValueError, match="No close price column"):
        close_series_from_history(history, "^GSPC")

