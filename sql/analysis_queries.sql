-- Query 01: Annual return by market.
-- Business question: Which market delivered the strongest return each year?
WITH year_end_prices AS (
    SELECT
        index_name,
        EXTRACT(year FROM trade_date) AS year,
        FIRST_VALUE(close_price) OVER (
            PARTITION BY index_name, EXTRACT(year FROM trade_date)
            ORDER BY trade_date
        ) AS first_close,
        LAST_VALUE(close_price) OVER (
            PARTITION BY index_name, EXTRACT(year FROM trade_date)
            ORDER BY trade_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_close
    FROM market_prices
)
SELECT DISTINCT
    index_name,
    year,
    ROUND(last_close / first_close - 1, 4) AS annual_return
FROM year_end_prices
ORDER BY year, annual_return DESC;

-- Query 02: Full-period return and volatility ranking.
-- Business question: Which markets delivered return, and how much volatility did investors accept?
WITH monthly_returns AS (
    SELECT
        index_name,
        trade_date,
        close_price / LAG(close_price) OVER (PARTITION BY index_name ORDER BY trade_date) - 1 AS monthly_return
    FROM market_prices
),
period_prices AS (
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
SELECT
    p.index_name,
    ROUND(MAX(p.last_close / p.first_close - 1), 4) AS cumulative_return,
    ROUND(STDDEV_SAMP(r.monthly_return) * SQRT(12), 4) AS annualized_volatility
FROM period_prices p
JOIN monthly_returns r USING (index_name)
WHERE r.monthly_return IS NOT NULL
GROUP BY p.index_name
ORDER BY cumulative_return DESC;

-- Query 03: Maximum drawdown by market.
-- Business question: Where was downside risk most severe?
WITH drawdown_path AS (
    SELECT
        index_name,
        trade_date,
        close_price,
        MAX(close_price) OVER (
            PARTITION BY index_name
            ORDER BY trade_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_peak
    FROM market_prices
)
SELECT
    index_name,
    trade_date AS trough_date,
    ROUND(close_price / running_peak - 1, 4) AS max_drawdown
FROM drawdown_path
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY index_name
    ORDER BY close_price / running_peak - 1
) = 1
ORDER BY max_drawdown;

-- Query 04: Return-to-risk score.
-- Business question: Which market produced the best return per unit of volatility?
WITH monthly_returns AS (
    SELECT
        index_name,
        trade_date,
        close_price / LAG(close_price) OVER (PARTITION BY index_name ORDER BY trade_date) - 1 AS monthly_return
    FROM market_prices
),
period_prices AS (
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
SELECT
    p.index_name,
    ROUND(MAX(p.last_close / p.first_close - 1), 4) AS cumulative_return,
    ROUND(STDDEV_SAMP(r.monthly_return) * SQRT(12), 4) AS annualized_volatility,
    ROUND(MAX(p.last_close / p.first_close - 1) / NULLIF(STDDEV_SAMP(r.monthly_return) * SQRT(12), 0), 2) AS return_to_risk
FROM period_prices p
JOIN monthly_returns r USING (index_name)
WHERE r.monthly_return IS NOT NULL
GROUP BY p.index_name
ORDER BY return_to_risk DESC;

-- Query 05: Market performance joined to latest macro snapshot.
-- Business question: What macro backdrop sits behind each selected equity market?
WITH latest_macro AS (
    SELECT
        country_code,
        country_name,
        indicator_name,
        indicator_value,
        year
    FROM macro_indicators
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY country_code, indicator_name
        ORDER BY year DESC
    ) = 1
),
market_returns AS (
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
SELECT
    mr.index_name,
    map.country_code,
    map.country_name,
    ROUND(MAX(mr.last_close / mr.first_close - 1), 4) AS cumulative_return,
    ROUND(MAX(CASE WHEN lm.indicator_name = 'GDP growth' THEN lm.indicator_value END), 2) AS latest_gdp_growth,
    ROUND(MAX(CASE WHEN lm.indicator_name = 'Inflation' THEN lm.indicator_value END), 2) AS latest_inflation,
    ROUND(MAX(CASE WHEN lm.indicator_name = 'Unemployment' THEN lm.indicator_value END), 2) AS latest_unemployment
FROM market_returns mr
JOIN market_country_map map USING (index_name)
LEFT JOIN latest_macro lm USING (country_code)
GROUP BY mr.index_name, map.country_code, map.country_name
ORDER BY cumulative_return DESC;

-- Query 06: 12-month rolling return.
-- Business question: Which markets had the strongest recent momentum?
SELECT
    index_name,
    trade_date,
    ROUND(close_price / LAG(close_price, 12) OVER (PARTITION BY index_name ORDER BY trade_date) - 1, 4) AS rolling_12m_return
FROM market_prices
QUALIFY rolling_12m_return IS NOT NULL
ORDER BY trade_date DESC, rolling_12m_return DESC;

-- Query 07: High-return but high-drawdown markets.
-- Business question: Which markets look attractive on return but uncomfortable on downside risk?
WITH monthly_returns AS (
    SELECT
        index_name,
        trade_date,
        close_price / LAG(close_price) OVER (PARTITION BY index_name ORDER BY trade_date) - 1 AS monthly_return
    FROM market_prices
),
period_return AS (
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
),
drawdowns AS (
    SELECT
        index_name,
        MIN(drawdown) AS max_drawdown
    FROM (
        SELECT
            index_name,
            close_price / MAX(close_price) OVER (
                PARTITION BY index_name
                ORDER BY trade_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) - 1 AS drawdown
        FROM market_prices
    )
    GROUP BY index_name
),
risk_summary AS (
    SELECT
        index_name,
        max_drawdown
    FROM drawdowns
)
SELECT
    pr.index_name,
    ROUND(MAX(pr.last_close / pr.first_close - 1), 4) AS cumulative_return,
    ROUND(MAX(r.max_drawdown), 4) AS max_drawdown,
    ROUND(STDDEV_SAMP(m.monthly_return) * SQRT(12), 4) AS annualized_volatility
FROM period_return pr
JOIN risk_summary r USING (index_name)
JOIN monthly_returns m USING (index_name)
WHERE m.monthly_return IS NOT NULL
GROUP BY pr.index_name
HAVING cumulative_return > 0 AND max_drawdown < -0.2
ORDER BY cumulative_return DESC;

-- Query 08: Return correlation matrix in long format.
-- Business question: Which markets move together?
WITH returns AS (
    SELECT
        index_name,
        trade_date,
        close_price / LAG(close_price) OVER (PARTITION BY index_name ORDER BY trade_date) - 1 AS monthly_return
    FROM market_prices
),
pairs AS (
    SELECT
        a.index_name AS market_a,
        b.index_name AS market_b,
        a.monthly_return AS return_a,
        b.monthly_return AS return_b
    FROM returns a
    JOIN returns b
        ON a.trade_date = b.trade_date
        AND a.index_name < b.index_name
    WHERE a.monthly_return IS NOT NULL
        AND b.monthly_return IS NOT NULL
)
SELECT
    market_a,
    market_b,
    ROUND(CORR(return_a, return_b), 3) AS return_correlation
FROM pairs
GROUP BY market_a, market_b
ORDER BY return_correlation DESC;

-- Query 09: Macro trend by country and indicator.
-- Business question: Which country-level macro indicators improved or worsened over the sample period?
WITH ranked_macro AS (
    SELECT
        country_code,
        country_name,
        indicator_name,
        year,
        indicator_value,
        FIRST_VALUE(indicator_value) OVER (
            PARTITION BY country_code, indicator_name
            ORDER BY year
        ) AS first_value,
        LAST_VALUE(indicator_value) OVER (
            PARTITION BY country_code, indicator_name
            ORDER BY year
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_value
    FROM macro_indicators
)
SELECT DISTINCT
    country_code,
    country_name,
    indicator_name,
    ROUND(last_value - first_value, 2) AS change_over_period
FROM ranked_macro
ORDER BY indicator_name, change_over_period DESC;

-- Query 10: Market returns versus GDP growth by year.
-- Business question: Do stronger equity-market years line up with stronger GDP growth?
WITH annual_prices AS (
    SELECT
        index_name,
        EXTRACT(year FROM trade_date) AS year,
        FIRST_VALUE(close_price) OVER (
            PARTITION BY index_name, EXTRACT(year FROM trade_date)
            ORDER BY trade_date
        ) AS first_close,
        LAST_VALUE(close_price) OVER (
            PARTITION BY index_name, EXTRACT(year FROM trade_date)
            ORDER BY trade_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_close
    FROM market_prices
),
annual_returns AS (
    SELECT DISTINCT
        index_name,
        year,
        last_close / first_close - 1 AS annual_return
    FROM annual_prices
),
gdp AS (
    SELECT
        country_code,
        year,
        indicator_value AS gdp_growth
    FROM macro_indicators
    WHERE indicator_name = 'GDP growth'
)
SELECT
    ar.index_name,
    map.country_code,
    ar.year,
    ROUND(ar.annual_return, 4) AS annual_return,
    ROUND(gdp.gdp_growth, 2) AS gdp_growth
FROM annual_returns ar
JOIN market_country_map map USING (index_name)
LEFT JOIN gdp
    ON map.country_code = gdp.country_code
    AND ar.year = gdp.year
ORDER BY ar.year, ar.annual_return DESC;
