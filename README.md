# Global Equity Market Performance & Risk Dashboard

全球主要股票指数表现与风险对比 Dashboard。This is a resume-ready data analysis portfolio project built with Python, pandas, Plotly, and Streamlit.

## Business Question / 业务问题

How have major global equity markets performed over the selected period, and which markets offer the best balance between return and downside risk?

在所选时间区间内，全球主要股票市场表现如何？哪些市场在收益、波动和回撤之间更具吸引力？

## What This Project Demonstrates / 项目亮点

- Data cleaning and validation for multi-market financial time series.
- Return, volatility, maximum drawdown, correlation, and return-to-risk analysis.
- A bilingual executive-style dashboard with interactive filters and automated insights.
- Reproducible sample data plus an optional online refresh script.
- Clear project structure, tests, and Git-friendly documentation.

## Dashboard Features / 功能

- KPI summary: best performer, weakest performer, highest volatility, deepest drawdown.
- Indexed performance chart with base value = 100.
- Risk lens with volatility, drawdown, and correlation heatmap.
- Automated English and Chinese insight bullets for interview storytelling.
- Raw data tab for transparency and reproducibility.

## Tech Stack / 技术栈

Python, pandas, NumPy, Plotly, Streamlit, yfinance, pytest, uv

## Project Structure / 项目结构

```text
.
├── app.py
├── data/
│   └── sample/
│       └── index_prices.csv
├── scripts/
│   └── update_data.py
├── src/
│   ├── data_loader.py
│   ├── insights.py
│   └── metrics.py
└── tests/
    ├── test_insights.py
    └── test_metrics.py
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

The app always works with the included sample data. If `data/live/index_prices.csv` exists, the dashboard uses it first.

## Data / 数据

The committed sample dataset contains monthly closing prices for five major equity indices from 2021 to 2024:

- S&P 500
- NASDAQ Composite
- FTSE 100
- Nikkei 225
- Hang Seng Index

The optional update script downloads public market data through `yfinance`. The project keeps live downloads out of Git by ignoring `data/live/`.

## Example Resume Bullet / 简历项目描述

Built a bilingual Streamlit dashboard to compare global equity index performance and risk using Python, pandas, and Plotly; implemented return, volatility, maximum drawdown, correlation, and automated insight generation with unit-tested analytics modules.

使用 Python、pandas、Plotly 和 Streamlit 构建中英双语全球股票指数分析 Dashboard，实现收益率、年化波动率、最大回撤、相关性和自动洞察生成，并为核心分析模块编写单元测试。

## GitHub Push / 推送到 GitHub

After creating an empty GitHub repository, run:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/global-market-analytics-dashboard.git
git branch -M main
git push -u origin main
```

