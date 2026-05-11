from pathlib import Path

import duckdb
import pytest

from src.data_loader import load_index_prices, price_matrix
from src.metrics import cumulative_returns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"
ANALYSIS_SQL = PROJECT_ROOT / "sql" / "analysis_queries.sql"


def _connect_with_schema() -> duckdb.DuckDBPyConnection:
    connection = duckdb.connect(database=":memory:")
    connection.execute(SCHEMA_SQL.read_text(encoding="utf-8"))
    return connection


def _analysis_statements() -> list[str]:
    sql = ANALYSIS_SQL.read_text(encoding="utf-8")
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def test_schema_views_load_sample_data():
    connection = _connect_with_schema()

    market_count = connection.execute("SELECT COUNT(*) FROM market_prices").fetchone()[0]
    macro_count = connection.execute("SELECT COUNT(*) FROM macro_indicators").fetchone()[0]
    mapping_count = connection.execute("SELECT COUNT(*) FROM market_country_map").fetchone()[0]

    assert market_count > 0
    assert macro_count > 0
    assert mapping_count == 5


def test_all_analysis_queries_execute_successfully():
    connection = _connect_with_schema()

    row_counts = []
    for statement in _analysis_statements():
        result = connection.execute(statement).fetchdf()
        row_counts.append(len(result))

    assert len(row_counts) == 10
    assert all(count >= 0 for count in row_counts)
    assert any(count > 0 for count in row_counts)


def test_sql_cumulative_return_matches_python_metric_for_sp500():
    connection = _connect_with_schema()
    sql_result = connection.execute(
        """
        WITH period_prices AS (
            SELECT
                index_name,
                FIRST_VALUE(close_price) OVER (
                    PARTITION BY index_name ORDER BY trade_date
                ) AS first_close,
                LAST_VALUE(close_price) OVER (
                    PARTITION BY index_name ORDER BY trade_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS last_close
            FROM market_prices
        )
        SELECT DISTINCT
            index_name,
            last_close / first_close - 1 AS cumulative_return
        FROM period_prices
        WHERE index_name = 'S&P 500'
        """
    ).fetchdf()

    prices = load_index_prices(prefer_live=False)
    python_returns = cumulative_returns(price_matrix(prices))

    assert sql_result.iloc[0]["cumulative_return"] == pytest.approx(python_returns["S&P 500"])


def test_market_macro_join_returns_expected_columns():
    connection = _connect_with_schema()
    result = connection.execute(
        """
        SELECT
            p.index_name,
            m.country_code,
            mi.indicator_name,
            mi.indicator_value
        FROM market_prices p
        JOIN market_country_map m USING (index_name)
        JOIN macro_indicators mi USING (country_code)
        WHERE mi.indicator_name = 'GDP growth'
        LIMIT 5
        """
    ).fetchdf()

    assert set(result.columns) == {"index_name", "country_code", "indicator_name", "indicator_value"}
    assert result["indicator_name"].eq("GDP growth").all()
