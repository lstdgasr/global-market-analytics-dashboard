from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import filter_prices, load_index_prices, price_matrix, resolve_data_source
from src.insights import generate_insights
from src.macro_insights import generate_macro_insights
from src.macro_loader import (
    COUNTRIES,
    attach_macro_to_summary,
    load_macro_data,
    resolve_macro_source,
)
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


@st.cache_data
def cached_macro(prefer_live: bool) -> pd.DataFrame:
    return load_macro_data(prefer_live=prefer_live)


def format_percent(value: float | None) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.1%}"


def format_number_percent(value: float | None) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.1f}%"


def build_market_label(prices: pd.DataFrame) -> pd.DataFrame:
    metadata = prices[["index_name", "ticker", "region", "currency"]].drop_duplicates()
    metadata["label"] = metadata["index_name"] + " · " + metadata["region"]
    return metadata.sort_values("index_name")


price_source = resolve_data_source(prefer_live=True)
macro_source = resolve_macro_source(prefer_live=True)
prices = cached_prices(prefer_live=True)
macro_data = cached_macro(prefer_live=True)
market_labels = build_market_label(prices)

st.title("Global Equity Market Performance & Macro Risk Dashboard")
st.caption("全球主要股票指数表现、风险与宏观背景对比 | A bilingual portfolio project for data analysis roles")

with st.sidebar:
    st.header("Filters / 筛选")
    st.caption(f"Market data: {price_source.label}")
    st.caption(f"Macro data: {macro_source.label}")
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

enriched_summary = attach_macro_to_summary(summary, macro_data)

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

tab_overview, tab_macro, tab_risk, tab_data = st.tabs(
    [
        "Market Brief / 市场简报",
        "Macro Context / 宏观背景",
        "Risk Lens / 风险视角",
        "Data / 数据",
    ]
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
    st.plotly_chart(trend_chart, width="stretch")

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
        width="stretch",
    )

with tab_macro:
    st.subheader("Macro Context / 宏观背景")
    st.write(
        "This view links market performance to official World Bank macro indicators. "
        "It is context for interpretation, not a causal model. / "
        "本页将市场表现与世界银行官方宏观指标关联，用于解释背景，不作为因果模型。"
    )

    selected_country_codes = sorted(set(enriched_summary["country_code"].dropna()) | {"CHN"})
    macro_filtered = macro_data[macro_data["country_code"].isin(selected_country_codes)]

    indicator_options = macro_filtered["indicator_name"].drop_duplicates().tolist()
    selected_indicators = st.multiselect(
        "Macro indicators / 宏观指标",
        options=indicator_options,
        default=indicator_options,
    )
    macro_chart_data = macro_filtered[macro_filtered["indicator_name"].isin(selected_indicators)]

    if not macro_chart_data.empty:
        macro_chart = px.line(
            macro_chart_data,
            x="year",
            y="value",
            color="country_name",
            facet_col="indicator_name",
            facet_col_wrap=2,
            markers=True,
            title="World Bank Macro Indicators / 世界银行宏观指标",
            labels={"year": "Year", "value": "Value", "country_name": "Country / Region"},
        )
        macro_chart.update_yaxes(matches=None)
        macro_chart.update_layout(legend_title_text="")
        st.plotly_chart(macro_chart, width="stretch")

    st.subheader("Macro-Aware Market Table / 市场与宏观对照表")
    macro_table = enriched_summary.copy()
    macro_table["cumulative_return"] = macro_table["cumulative_return"].map(format_percent)
    macro_table["annualized_volatility"] = macro_table["annualized_volatility"].map(format_percent)
    macro_table["max_drawdown"] = macro_table["max_drawdown"].map(format_percent)
    for column in ["GDP growth", "Inflation", "Unemployment", "Market capitalization to GDP"]:
        if column in macro_table:
            macro_table[column] = macro_table[column].map(format_number_percent)

    st.dataframe(
        macro_table[
            [
                "index_name",
                "country_code",
                "country_name",
                "cumulative_return",
                "annualized_volatility",
                "max_drawdown",
                "GDP growth",
                "Inflation",
                "Unemployment",
                "Market capitalization to GDP",
            ]
        ].rename(
            columns={
                "index_name": "Market",
                "country_code": "Country Code",
                "country_name": "Country / Region",
                "cumulative_return": "Cumulative Return",
                "annualized_volatility": "Annualized Volatility",
                "max_drawdown": "Max Drawdown",
            }
        ),
        width="stretch",
    )

    st.subheader("Macro Insights / 宏观洞察")
    for insight in generate_macro_insights(enriched_summary):
        st.write(f"- {insight}")

    with st.expander("Country coverage / 国家与地区覆盖"):
        coverage = pd.DataFrame(
            [{"country_code": code, "country_name": name} for code, name in COUNTRIES.items()]
        )
        st.dataframe(coverage, width="stretch")

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
    risk_cols[0].plotly_chart(vol_chart, width="stretch")

    drawdown_chart = px.bar(
        drawdown,
        x="Market",
        y="Max drawdown",
        title="Maximum Drawdown / 最大回撤",
        text_auto=".1%",
    )
    drawdown_chart.update_yaxes(tickformat=".0%")
    risk_cols[1].plotly_chart(drawdown_chart, width="stretch")

    corr = correlation_matrix(matrix)
    heatmap = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        title="Return Correlation Matrix / 收益率相关性矩阵",
    )
    st.plotly_chart(heatmap, width="stretch")

with tab_data:
    st.subheader("Dataset Metadata / 数据说明")
    st.write(
        "The app uses reproducible sample datasets by default and switches to `data/live/` files "
        "after running the update scripts. / 默认使用可复现样例数据；运行更新脚本后会优先使用在线刷新数据。"
    )
    st.write("- Market source: Yahoo Finance through `yfinance` / 市场数据：Yahoo Finance")
    st.write("- Macro source: World Bank Indicators API / 宏观数据：世界银行 Indicators API")
    st.dataframe(filtered, width="stretch")
    st.dataframe(macro_data, width="stretch")
