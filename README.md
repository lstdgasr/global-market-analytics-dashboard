# Global Equity Market Performance & Macro Risk Dashboard

全球主要股票指数表现、风险与宏观背景对比 Dashboard。This is a resume-ready data analysis portfolio project built with Python, pandas, Plotly, Streamlit, Yahoo Finance data, and World Bank macro indicators.

## Business Question / 业务问题

How have major global equity markets performed, and how does that performance compare with macroeconomic conditions such as GDP growth, inflation, unemployment, and market depth?

全球主要股票市场表现如何？这些表现与 GDP 增速、通胀、失业率、资本市场深度等宏观背景是否一致？

## What This Project Demonstrates / 项目亮点

- Multi-source data pipeline combining market prices and official World Bank macro indicators.
- Data cleaning and validation for financial time series and country-level macro data.
- Return, volatility, maximum drawdown, correlation, macro context, and return-to-risk analysis.
- A bilingual executive-style dashboard with interactive filters and automated insight generation.
- Reproducible sample datasets plus optional online refresh scripts.
- Unit-tested analytics modules and Git-friendly project structure.

## Data Sources / 数据来源

- Market data: Yahoo Finance through `yfinance`.
- Macro data: World Bank Indicators API, no API key required.

World Bank indicators used:

| Indicator | Code | Meaning |
| --- | --- | --- |
| GDP growth | `NY.GDP.MKTP.KD.ZG` | Annual real GDP growth |
| Inflation | `FP.CPI.TOTL.ZG` | Consumer price inflation |
| Unemployment | `SL.UEM.TOTL.ZS` | Unemployment rate |
| Market capitalization to GDP | `CM.MKT.LCAP.GD.ZS` | Listed-company market value as a share of GDP |

## Dashboard Features / 功能

- KPI summary: best performer, weakest performer, highest volatility, deepest drawdown.
- Indexed market performance chart with base value = 100.
- Macro context tab linking each market to country or regional indicators.
- Risk lens with volatility, drawdown, and return-correlation heatmap.
- Automated English and Chinese insight bullets for interview storytelling.
- Raw data tab for transparency and reproducibility.

## Tech Stack / 技术栈

Python, pandas, NumPy, Plotly, Streamlit, yfinance, requests, pytest, uv

## Project Structure / 项目结构

```text
.
|-- app.py
|-- data/
|   |-- sample/
|   |   |-- index_prices.csv
|   |   `-- macro_indicators.csv
|-- scripts/
|   |-- update_data.py
|   `-- update_macro_data.py
|-- src/
|   |-- data_loader.py
|   |-- insights.py
|   |-- macro_insights.py
|   |-- macro_loader.py
|   `-- metrics.py
`-- tests/
    |-- test_data_loader.py
    |-- test_insights.py
    |-- test_macro_insights.py
    |-- test_macro_loader.py
    `-- test_metrics.py
```

## Run Locally / 本地运行

```powershell
uv sync --python 3.10
uv run streamlit run app.py
```

Run tests:

```powershell
uv run pytest
```

Optional: refresh online market data from Yahoo Finance:

```powershell
uv run python scripts/update_data.py --start 2021-01-01
```

Optional: refresh macro data from the World Bank:

```powershell
uv run python scripts/update_macro_data.py --start-year 2020 --end-year 2024
```

The app always works with the included sample data. If files exist under `data/live/`, the dashboard uses those refreshed datasets first.

## Example Resume Bullet / 简历项目描述

Built a bilingual Streamlit dashboard combining global equity index data with official World Bank macro indicators; implemented market return, volatility, drawdown, correlation, GDP/inflation/unemployment context, and automated insight generation with unit-tested Python analytics modules.

使用 Python、pandas、Plotly 和 Streamlit 构建中英双语全球股票指数分析 Dashboard，结合 Yahoo Finance 市场数据与世界银行宏观指标，实现收益率、年化波动率、最大回撤、相关性、GDP/通胀/失业率背景分析和自动洞察生成，并为核心模块编写单元测试。

