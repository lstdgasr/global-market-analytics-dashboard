# SQL Analytics Layer

This folder shows how the project can be analyzed with SQL before the results are visualized in Python and Streamlit.

## Why DuckDB

DuckDB is used because it can query CSV files directly, supports CTEs and window functions, and feels close to SQL used in analytics roles.

Run from the repository root:

```powershell
uv run python -m pytest tests/test_sql_layer.py
```

Or open DuckDB manually:

```sql
.read sql/schema.sql
.read sql/analysis_queries.sql
```

## Files

- `schema.sql`: creates views over the sample market prices, macro indicators, and market-country mapping.
- `analysis_queries.sql`: contains 10 interview-ready business queries.

## Query Portfolio

1. Annual return by market: yearly performance ranking.
2. Full-period return and volatility: return versus accepted risk.
3. Maximum drawdown by market: downside-risk comparison.
4. Return-to-risk score: simple efficiency ranking.
5. Market performance joined to macro snapshot: SQL Join across market and World Bank data.
6. 12-month rolling return: momentum using `LAG`.
7. High-return but high-drawdown markets: risk flag query with CTEs.
8. Return correlation matrix: pairwise market co-movement.
9. Macro trend by country and indicator: macro improvement or deterioration.
10. Market returns versus GDP growth by year: market-macro alignment table.

## Resume Wording

Built a SQL analytics layer with DuckDB, CTEs, window functions, aggregations, and multi-table joins to analyze global index returns, volatility, drawdown, correlations, and World Bank macro indicators before visualizing the results in Streamlit.

