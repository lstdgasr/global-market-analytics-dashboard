from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import filter_prices, load_index_prices, price_matrix, resolve_data_source
from src.insights import generate_insights
from src.metrics import (
    annualized_volatility,
    correlation_matrix,
    max_drawdowns,
    normalized_prices,
    risk_return_summary,
)


st.set_page_config(
    page_title="Global Market Analytics",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def cached_prices(prefer_live: bool) -> pd.DataFrame:
    return load_index_prices(prefer_live=prefer_live)


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def build_market_label(prices: pd.DataFrame) -> pd.DataFrame:
    metadata = prices[["index_name", "ticker", "region", "currency"]].drop_duplicates()
    metadata["label"] = metadata["index_name"] + " · " + metadata["region"]
    return metadata.sort_values("index_name")


source = resolve_data_source(prefer_live=True)
prices = cached_prices(prefer_live=True)
market_labels = build_market_label(prices)

st.title("Global Equity Market Performance & Risk Dashboard")
st.caption("全球主要股票指数表现与风险对比 | A bilingual portfolio project for data analysis roles")

with st.sidebar:
    st.header("Filters / 筛选")
    st.caption(f"Data source: {source.label}")
    selected_markets = st.multiselect(
        "Markets / 市场",
        options=market_labels["index_name"].tolist(),
        default=market_labels["index_name"].tolist(),
    )
    min_date = prices["date"].min().date()
    max_date = prices["date"].max().date()
    selected_dates = st.date_input(
        "Date range / 日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

filtered = filter_prices(
    prices,
    markets=selected_markets,
    start_date=pd.Timestamp(start_date),
    end_date=pd.Timestamp(end_date),
)
matrix = price_matrix(filtered)
summary = risk_return_summary(matrix)

if filtered.empty or matrix.empty or summary.empty:
    st.warning("No data is available for the selected filters. / 当前筛选条件下没有可用数据。")
    st.stop()

best_market = summary["cumulative_return"].idxmax()
worst_market = summary["cumulative_return"].idxmin()
riskiest_market = summary["annualized_volatility"].idxmax()
deepest_drawdown = summary["max_drawdown"].idxmin()

metric_cols = st.columns(4)
metric_cols[0].metric(
    "Best Performer / 最佳市场",
    best_market,
    format_percent(summary.loc[best_market, "cumulative_return"]),
)
metric_cols[1].metric(
    "Weakest Performer / 最弱市场",
    worst_market,
    format_percent(summary.loc[worst_market, "cumulative_return"]),
)
metric_cols[2].metric(
    "Highest Volatility / 最高波动",
    riskiest_market,
    format_percent(summary.loc[riskiest_market, "annualized_volatility"]),
)
metric_cols[3].metric(
    "Deepest Drawdown / 最大回撤",
    deepest_drawdown,
    format_percent(summary.loc[deepest_drawdown, "max_drawdown"]),
)

tab_overview, tab_risk, tab_data = st.tabs(
    ["Market Brief / 市场简报", "Risk Lens / 风险视角", "Data / 数据"]
)

with tab_overview:
    normalized = normalized_prices(matrix).reset_index().melt(
        id_vars="date",
        var_name="Market",
        value_name="Indexed value",
    )
    trend_chart = px.line(
        normalized,
        x="date",
        y="Indexed value",
        color="Market",
        title="Indexed Performance, Base = 100 / 标准化走势",
        labels={"date": "Date", "Indexed value": "Indexed value"},
    )
    trend_chart.update_layout(legend_title_text="", hovermode="x unified")
    st.plotly_chart(trend_chart, use_container_width=True)

    st.subheader("Executive Insights / 管理层摘要")
    for insight in generate_insights(summary):
        st.write(f"- {insight}")

    display_summary = summary.copy()
    for column in ["cumulative_return", "annualized_volatility", "max_drawdown"]:
        display_summary[column] = display_summary[column].map(format_percent)
    display_summary["return_to_risk"] = display_summary["return_to_risk"].map(lambda value: f"{value:.2f}")
    st.dataframe(
        display_summary.rename(
            columns={
                "cumulative_return": "Cumulative Return",
                "annualized_volatility": "Annualized Volatility",
                "max_drawdown": "Max Drawdown",
                "return_to_risk": "Return / Risk",
            }
        ),
        use_container_width=True,
    )

with tab_risk:
    risk_cols = st.columns(2)
    vol = annualized_volatility(matrix).reset_index()
    vol.columns = ["Market", "Annualized volatility"]
    drawdown = max_drawdowns(matrix).reset_index()
    drawdown.columns = ["Market", "Max drawdown"]

    vol_chart = px.bar(
        vol,
        x="Market",
        y="Annualized volatility",
        title="Annualized Volatility / 年化波动率",
        text_auto=".1%",
    )
    vol_chart.update_yaxes(tickformat=".0%")
    risk_cols[0].plotly_chart(vol_chart, use_container_width=True)

    drawdown_chart = px.bar(
        drawdown,
        x="Market",
        y="Max drawdown",
        title="Maximum Drawdown / 最大回撤",
        text_auto=".1%",
    )
    drawdown_chart.update_yaxes(tickformat=".0%")
    risk_cols[1].plotly_chart(drawdown_chart, use_container_width=True)

    corr = correlation_matrix(matrix)
    heatmap = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        title="Return Correlation Matrix / 收益率相关性矩阵",
    )
    st.plotly_chart(heatmap, use_container_width=True)

with tab_data:
    st.subheader("Dataset Metadata / 数据说明")
    st.write(
        "The app uses a reproducible sample dataset by default and switches to `data/live/index_prices.csv` "
        "after running the update script. / 默认使用可复现样例数据；运行更新脚本后会优先使用在线刷新数据。"
    )
    st.dataframe(filtered, use_container_width=True)

