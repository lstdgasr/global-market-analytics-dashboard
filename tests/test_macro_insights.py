import pandas as pd

from src.macro_insights import generate_macro_insights


def test_generate_macro_insights_handles_empty_data():
    insights = generate_macro_insights(pd.DataFrame())

    assert "No macro context" in insights[0]
    assert "没有可用宏观背景数据" in insights[0]


def test_generate_macro_insights_outputs_bilingual_context():
    enriched = pd.DataFrame(
        {
            "index_name": ["S&P 500", "FTSE 100", "Nikkei 225"],
            "cumulative_return": [0.2, 0.05, 0.12],
            "GDP growth": [2.8, 1.1, 0.2],
            "Inflation": [3.0, 5.2, 2.7],
            "Unemployment": [4.1, 4.3, 2.6],
            "Market capitalization to GDP": [157.4, 97.3, 126.2],
        }
    )

    insights = generate_macro_insights(enriched)
    joined = "\n".join(insights)

    assert "GDP growth" in joined
    assert "通胀背景" in joined
    assert "资本市场深度" in joined

