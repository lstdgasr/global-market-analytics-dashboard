from __future__ import annotations

import pandas as pd


def _pct(value: float) -> str:
    return f"{value:.1f}%"


def generate_macro_insights(enriched_summary: pd.DataFrame) -> list[str]:
    if enriched_summary.empty:
        return [
            "No macro context is available for the selected markets. / 当前筛选市场没有可用宏观背景数据。",
        ]

    insights: list[str] = []
    if "GDP growth" in enriched_summary and enriched_summary["GDP growth"].notna().any():
        best_growth_row = enriched_summary.loc[enriched_summary["GDP growth"].idxmax()]
        insights.append(
            f"{best_growth_row['index_name']} is linked to the strongest recent GDP growth "
            f"({_pct(best_growth_row['GDP growth'])}), adding macro support to the market story. / "
            f"{best_growth_row['index_name']} 对应经济体近期 GDP 增速最高（{_pct(best_growth_row['GDP growth'])}），"
            "为市场表现提供了宏观支撑。"
        )

    if "Inflation" in enriched_summary and enriched_summary["Inflation"].notna().any():
        high_inflation_row = enriched_summary.loc[enriched_summary["Inflation"].idxmax()]
        insights.append(
            f"{high_inflation_row['index_name']} has the highest inflation backdrop "
            f"({_pct(high_inflation_row['Inflation'])}), which may pressure valuation and policy expectations. / "
            f"{high_inflation_row['index_name']} 对应通胀背景最高（{_pct(high_inflation_row['Inflation'])}），"
            "可能影响估值和政策预期。"
        )

    if "Unemployment" in enriched_summary and enriched_summary["Unemployment"].notna().any():
        low_unemployment_row = enriched_summary.loc[enriched_summary["Unemployment"].idxmin()]
        insights.append(
            f"{low_unemployment_row['index_name']} has the tightest labor-market backdrop "
            f"({_pct(low_unemployment_row['Unemployment'])} unemployment). / "
            f"{low_unemployment_row['index_name']} 对应劳动力市场最紧（失业率 {_pct(low_unemployment_row['Unemployment'])}）。"
        )

    if "Market capitalization to GDP" in enriched_summary and enriched_summary["Market capitalization to GDP"].notna().any():
        depth_row = enriched_summary.loc[enriched_summary["Market capitalization to GDP"].idxmax()]
        insights.append(
            f"{depth_row['index_name']} sits in the deepest listed-equity market context "
            f"({_pct(depth_row['Market capitalization to GDP'])} of GDP), useful for discussing market depth. / "
            f"{depth_row['index_name']} 对应上市公司市值/GDP 最高（{_pct(depth_row['Market capitalization to GDP'])}），"
            "可用于说明资本市场深度。"
        )

    if "cumulative_return" in enriched_summary and "GDP growth" in enriched_summary:
        valid = enriched_summary.dropna(subset=["cumulative_return", "GDP growth"])
        if len(valid) >= 3:
            corr = valid["cumulative_return"].corr(valid["GDP growth"])
            if pd.notna(corr):
                insights.append(
                    f"Across selected markets, the simple return-vs-GDP-growth correlation is {corr:.2f}; "
                    "treat it as context rather than causality. / "
                    f"所选市场中，收益与 GDP 增速的简单相关系数为 {corr:.2f}；这更适合作为背景解释，而非因果结论。"
                )

    return insights[:5]

