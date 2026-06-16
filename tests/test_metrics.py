from __future__ import annotations

import pandas as pd

from src.data_loader import MarketingData
from src.metrics import budget_totals_by_brand, build_executive_kpis, social_by_week


def test_build_executive_kpis_success_case() -> None:
    data = MarketingData(
        acquisition=pd.DataFrame({"new_customers": [10, 15], "brand": ["A", "B"], "report_year": [2026, 2026]}),
        retention=pd.DataFrame({"uses": [3], "brand": ["A"], "report_year": [2026]}),
        app=pd.DataFrame(),
        newsletter=pd.DataFrame(),
        satisfaction=pd.DataFrame({"brand": ["A"], "report_year": [2026], "calendar_week": [23], "google_rating": [4.9]}),
        social=pd.DataFrame({"views": [1000], "interactions": [100], "brand": ["A"], "report_year": [2026]}),
        budget_categories=pd.DataFrame(
            {
                "brand": ["A"],
                "report_year": [2026],
                "category": ["SUMME"],
                "planned": [1000.0],
                "used": [250.0],
                "available": [750.0],
                "is_total": [True],
            }
        ),
        budget_monthly=pd.DataFrame(),
        bookings=pd.DataFrame(),
    )

    kpis = build_executive_kpis(data)

    assert kpis[0].value == "250 EUR / 1.000 EUR"
    assert kpis[1].value == "25"
    assert kpis[3].value == "10,0%"
    assert kpis[0].delta == "○ kein Vormonat"


def test_budget_totals_and_social_week_labels() -> None:
    data = MarketingData(
        acquisition=pd.DataFrame(),
        retention=pd.DataFrame(),
        app=pd.DataFrame(),
        newsletter=pd.DataFrame(),
        satisfaction=pd.DataFrame(),
        social=pd.DataFrame(
            {
                "brand": ["Gemüsegärtner"],
                "report_year": [2026],
                "calendar_week": [23],
                "views": [500],
                "interactions": [50],
                "new_followers": [5],
                "followers": [9415],
            }
        ),
        budget_categories=pd.DataFrame(
            {
                "brand": ["Gemüsegärtner"],
                "report_year": [2026],
                "planned": [1000.0],
                "used": [500.0],
                "available": [500.0],
                "is_total": [True],
            }
        ),
        budget_monthly=pd.DataFrame(),
        bookings=pd.DataFrame(),
    )

    assert budget_totals_by_brand(data).loc[0, "usage_rate"] == 0.5
    assert social_by_week(data).loc[0, "week_label"] == "2026-KW 23"


def test_build_executive_kpis_adds_monthly_trend_delta() -> None:
    data = MarketingData(
        acquisition=pd.DataFrame(
            {
                "brand": ["Gemüsegärtner", "Gemüsegärtner"],
                "report_year": [2026, 2026],
                "calendar_week": [19, 23],
                "new_customers": [10, 15],
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

    kpis = build_executive_kpis(data)

    assert kpis[1].delta == "▲ 50,0%"
