from __future__ import annotations

import pandas as pd


def _format_percent(value: float) -> str:
    return f"{value:.1%}"


def generate_insights(summary: pd.DataFrame) -> list[str]:
    if summary.empty:
        return [
            "No valid market data is available for the selected period. / 当前筛选区间没有可用市场数据。",
        ]

    insights: list[str] = []
    best_market = summary["cumulative_return"].idxmax()
    worst_market = summary["cumulative_return"].idxmin()
    riskiest_market = summary["annualized_volatility"].idxmax()
    deepest_drawdown = summary["max_drawdown"].idxmin()

    best_return = summary.loc[best_market, "cumulative_return"]
    worst_return = summary.loc[worst_market, "cumulative_return"]
    risk_value = summary.loc[riskiest_market, "annualized_volatility"]
    drawdown_value = summary.loc[deepest_drawdown, "max_drawdown"]

    insights.append(
        f"{best_market} led the selected universe with a cumulative return of "
        f"{_format_percent(best_return)}. / {best_market} 在所选市场中表现最佳，累计收益为 {_format_percent(best_return)}。"
    )

    if best_market != worst_market:
        insights.append(
            f"{worst_market} lagged with a cumulative return of {_format_percent(worst_return)}, "
            "highlighting regional dispersion. / "
            f"{worst_market} 累计收益为 {_format_percent(worst_return)}，体现出区域市场分化。"
        )

    insights.append(
        f"{riskiest_market} showed the highest annualized volatility at {_format_percent(risk_value)}. / "
        f"{riskiest_market} 年化波动率最高，为 {_format_percent(risk_value)}。"
    )

    insights.append(
        f"The deepest drawdown occurred in {deepest_drawdown} at {_format_percent(drawdown_value)}, "
        "which is the key downside risk to monitor. / "
        f"最大回撤出现在 {deepest_drawdown}，幅度为 {_format_percent(drawdown_value)}，是需要重点关注的下行风险。"
    )

    if "return_to_risk" in summary.columns and summary["return_to_risk"].notna().any():
        efficient_market = summary["return_to_risk"].idxmax()
        efficiency = summary.loc[efficient_market, "return_to_risk"]
        insights.append(
            f"{efficient_market} had the strongest return-to-risk profile ({efficiency:.2f}). / "
            f"{efficient_market} 的收益风险比最高（{efficiency:.2f}）。"
        )

    return insights[:5]

