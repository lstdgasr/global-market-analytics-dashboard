-- DuckDB schema for the portfolio SQL analytics layer.
-- Run from the repository root so relative CSV paths resolve correctly.

CREATE OR REPLACE VIEW market_prices AS
SELECT
    CAST(date AS DATE) AS trade_date,
    index_name,
    ticker,
    region,
    currency,
    CAST(close AS DOUBLE) AS close_price
FROM read_csv_auto('data/sample/index_prices.csv', header = true);

CREATE OR REPLACE VIEW macro_indicators AS
SELECT
    country_code,
    country_name,
    CAST(year AS INTEGER) AS year,
    indicator_code,
    indicator_name,
    CAST(value AS DOUBLE) AS indicator_value,
    unit,
    category
FROM read_csv_auto('data/sample/macro_indicators.csv', header = true);

CREATE OR REPLACE VIEW market_country_map AS
SELECT *
FROM (
    VALUES
        ('S&P 500', 'USA', 'United States'),
        ('NASDAQ Composite', 'USA', 'United States'),
        ('FTSE 100', 'GBR', 'United Kingdom'),
        ('Nikkei 225', 'JPN', 'Japan'),
        ('Hang Seng Index', 'HKG', 'Hong Kong SAR, China')
) AS mapping(index_name, country_code, country_name);

