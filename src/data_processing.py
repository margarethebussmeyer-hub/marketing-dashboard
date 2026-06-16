from __future__ import annotations

import re

import pandas as pd

from src.data_loader import MarketingData


MIN_DASHBOARD_YEAR = 2025


def filter_dashboard_data(data: MarketingData, brands: list[str], years: list[int]) -> MarketingData:
    """Filter all dashboard tables by brand and year."""

    return MarketingData(
        acquisition=_filter(data.acquisition, brands, years),
        retention=_filter(data.retention, brands, years),
        app=_filter(data.app, brands, years),
        newsletter=_filter(data.newsletter, brands, years),
        satisfaction=_filter(data.satisfaction, brands, years),
        social=_filter(data.social, brands, years),
        budget_categories=_filter(data.budget_categories, brands, years),
        budget_monthly=_filter(data.budget_monthly, brands, years),
        bookings=_filter(data.bookings, brands, years),
    )


def available_brands(data: MarketingData) -> list[str]:
    brands = set()
    for frame in _frames(data):
        if "brand" in frame:
            brands.update(frame["brand"].dropna().unique().tolist())
    return sorted(brands)


def available_years(data: MarketingData) -> list[int]:
    years = set()
    for frame in _frames(data):
        if "report_year" in frame:
            years.update(int(year) for year in frame["report_year"].dropna().unique().tolist())
    return sorted(year for year in years if year >= MIN_DASHBOARD_YEAR)


def build_discount_code_overview(retention: pd.DataFrame) -> pd.DataFrame:
    """Create a yearly list of voucher and discount codes."""

    if retention.empty or "voucher_name" not in retention.columns:
        return pd.DataFrame(columns=["brand", "report_year", "discount_code", "uses", "channel", "period"])

    frame = retention.dropna(subset=["voucher_name"]).copy()
    frame["discount_code"] = frame["voucher_name"].map(_clean_code)
    frame = frame[frame["discount_code"] != ""].copy()
    if frame.empty:
        return pd.DataFrame(columns=["brand", "report_year", "discount_code", "uses", "channel", "period"])

    frame["uses"] = pd.to_numeric(frame.get("uses"), errors="coerce").fillna(0)
    overview = (
        frame.groupby(["brand", "report_year", "discount_code"], as_index=False)
        .agg(
            uses=("uses", "sum"),
            channel=("channel", lambda values: ", ".join(sorted(set(str(value) for value in values.dropna())))),
            period=("start_date", _period_label),
        )
        .sort_values(["brand", "report_year", "uses"], ascending=[True, True, False])
        .reset_index(drop=True)
    )
    return overview


def top_booking_suppliers(bookings: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    if bookings.empty:
        return pd.DataFrame(columns=["supplier", "amount"])
    return (
        bookings.groupby("supplier", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head(limit)
    )


def _filter(frame: pd.DataFrame, brands: list[str], years: list[int]) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    result = frame.copy()
    if "brand" in result:
        result = result[result["brand"].isin(brands)]
    if "report_year" in result:
        result = result[
            (result["report_year"] >= MIN_DASHBOARD_YEAR)
            & result["report_year"].isin(years)
        ]
    return result.copy()


def _frames(data: MarketingData) -> list[pd.DataFrame]:
    return [
        data.acquisition,
        data.retention,
        data.app,
        data.newsletter,
        data.satisfaction,
        data.social,
        data.budget_categories,
        data.budget_monthly,
        data.bookings,
    ]


def _clean_code(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip(" .;:")
    if text.lower() in {"/", "-", "kein aktueller code"}:
        return ""
    return text


def _period_label(values: pd.Series) -> str:
    dates = pd.to_datetime(values.dropna(), errors="coerce").dropna()
    if dates.empty:
        return ""
    return ", ".join(sorted({date.strftime("%d.%m.%Y") for date in dates}))
