import pandas as pd

from src.insights import generate_insights


def test_generate_insights_handles_empty_summary():
    insights = generate_insights(pd.DataFrame())

    assert len(insights) == 1
    assert "No valid market data" in insights[0]
    assert "没有可用市场数据" in insights[0]


def test_generate_insights_mentions_best_riskiest_and_drawdown_markets():
    summary = pd.DataFrame(
        {
            "cumulative_return": {"S&P 500": 0.2, "Hang Seng Index": -0.1},
            "annualized_volatility": {"S&P 500": 0.15, "Hang Seng Index": 0.28},
            "max_drawdown": {"S&P 500": -0.12, "Hang Seng Index": -0.35},
            "return_to_risk": {"S&P 500": 1.33, "Hang Seng Index": -0.36},
        }
    )

    insights = generate_insights(summary)
    joined = "\n".join(insights)

    assert "S&P 500 led" in joined
    assert "Hang Seng Index" in joined
    assert "年化波动率最高" in joined
    assert "最大回撤" in joined

