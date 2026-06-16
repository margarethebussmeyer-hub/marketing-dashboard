from __future__ import annotations

import pandas as pd

from src.charts import budget_monthly_usage_chart


def test_budget_monthly_usage_chart_builds_planned_and_used_bars() -> None:
    frame = pd.DataFrame(
        {
            "brand": ["Gemüsegärtner", "Gemüsegärtner"],
            "report_year": [2026, 2026],
            "category": ["SUMME", "SUMME"],
            "month": ["Januar", "Januar"],
            "month_number": [1, 1],
            "metric": ["Geplant", "Verwendet"],
            "amount": [1000.0, 750.0],
            "is_total": [True, True],
        }
    )

    figure = budget_monthly_usage_chart(frame)

    assert len(figure.data) == 2
