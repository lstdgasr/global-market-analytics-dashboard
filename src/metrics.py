from __future__ import annotations

import math

import numpy as np
import pandas as pd


def infer_periods_per_year(index: pd.Index) -> int:
    dates = pd.to_datetime(index).sort_values()
    if len(dates) < 3:
        return 12

    gaps = dates.to_series().diff().dropna().dt.days
    median_gap = float(gaps.median())
    if median_gap <= 2:
        return 252
    if median_gap <= 10:
        return 52
    if median_gap <= 45:
        return 12
    if median_gap <= 120:
        return 4
    return 1


def normalized_prices(price_matrix: pd.DataFrame, base: float = 100.0) -> pd.DataFrame:
    if price_matrix.empty:
        return pd.DataFrame(index=price_matrix.index, columns=price_matrix.columns)
    first_valid = price_matrix.apply(lambda column: column.dropna().iloc[0] if column.notna().any() else np.nan)
    return price_matrix.divide(first_valid).multiply(base)


def returns_matrix(price_matrix: pd.DataFrame) -> pd.DataFrame:
    if price_matrix.empty:
        return pd.DataFrame(index=price_matrix.index, columns=price_matrix.columns)
    return price_matrix.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).dropna(how="all")


def cumulative_returns(price_matrix: pd.DataFrame) -> pd.Series:
    if price_matrix.empty:
        return pd.Series(dtype=float)
    first = price_matrix.apply(lambda column: column.dropna().iloc[0] if column.notna().any() else np.nan)
    last = price_matrix.apply(lambda column: column.dropna().iloc[-1] if column.notna().any() else np.nan)
    return last.divide(first).subtract(1.0).dropna().sort_values(ascending=False)


def annualized_volatility(price_matrix: pd.DataFrame) -> pd.Series:
    returns = returns_matrix(price_matrix)
    if returns.empty:
        return pd.Series(0.0, index=price_matrix.columns, dtype=float)
    periods = infer_periods_per_year(price_matrix.index)
    return returns.std(skipna=True).multiply(math.sqrt(periods)).fillna(0.0).sort_values(ascending=False)


def max_drawdowns(price_matrix: pd.DataFrame) -> pd.Series:
    if price_matrix.empty:
        return pd.Series(dtype=float)
    running_peak = price_matrix.cummax()
    drawdown = price_matrix.divide(running_peak).subtract(1.0)
    return drawdown.min(skipna=True).fillna(0.0).sort_values()


def correlation_matrix(price_matrix: pd.DataFrame) -> pd.DataFrame:
    returns = returns_matrix(price_matrix)
    if returns.empty:
        return pd.DataFrame(index=price_matrix.columns, columns=price_matrix.columns, dtype=float)
    return returns.corr()


def risk_return_summary(price_matrix: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame(
        {
            "cumulative_return": cumulative_returns(price_matrix),
            "annualized_volatility": annualized_volatility(price_matrix),
            "max_drawdown": max_drawdowns(price_matrix),
        }
    )
    if summary.empty:
        return summary
    summary["return_to_risk"] = np.where(
        summary["annualized_volatility"] > 0,
        summary["cumulative_return"] / summary["annualized_volatility"],
        np.nan,
    )
    return summary.sort_values("cumulative_return", ascending=False)

