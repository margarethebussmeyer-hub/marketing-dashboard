from __future__ import annotations

import pandas as pd

from src.data_loader import MarketingData
from src.data_processing import available_years, filter_dashboard_data


def test_dashboard_filters_exclude_years_before_2025() -> None:
    data = MarketingData(
        acquisition=pd.DataFrame(
            {
                "brand": ["Gemüsegärtner", "Gemüsegärtner", "Gemüsegärtner"],
                "report_year": [2024, 2025, 2026],
                "new_customers": [1, 2, 3],
            }
        ),
        retention=pd.DataFrame(),
        app=pd.DataFrame(),
        newsletter=pd.DataFrame(),
        satisfaction=pd.DataFrame(),
        social=pd.DataFrame(),
        budget_categories=pd.DataFrame(),
        budget_monthly=pd.DataFrame(),
        bookings=pd.DataFrame(),
    )

    assert available_years(data) == [2025, 2026]

    filtered = filter_dashboard_data(data, ["Gemüsegärtner"], [2024, 2025, 2026])

    assert filtered.acquisition["report_year"].tolist() == [2025, 2026]
