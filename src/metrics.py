from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.data_loader import MarketingData


@dataclass(frozen=True)
class Kpi:
    label: str
    value: str
    help_text: str
    delta: str | None = None
    delta_color: str = "normal"


@dataclass(frozen=True)
class Trend:
    label: str
    color: str = "normal"


def build_executive_kpis(data: MarketingData) -> list[Kpi]:
    """Build the most relevant top-level KPIs for marketing management."""

    budget_total = _budget_total(data.budget_categories)
    new_customers = _sum(data.acquisition, "new_customers")
    views = _sum(data.social, "views")
    interactions = _sum(data.social, "interactions")
    voucher_uses = _sum(data.retention, "uses")
    latest_rating = _latest_average(data.satisfaction, "google_rating")
    trends = _build_monthly_trends(data)

    return [
        Kpi(
            "Budget verbraucht",
            f"{_format_currency(budget_total['used'])} / {_format_currency(budget_total['planned'])}",
            f"Verbleibend: {_format_currency(budget_total['available'])}",
            trends["budget_used"].label,
            trends["budget_used"].color,
        ),
        Kpi("Neukunden", _format_number(new_customers), "Summe aus Neukundengewinnung", trends["new_customers"].label, trends["new_customers"].color),
        Kpi("Social Aufrufe", _format_number(views), "Summe der gemessenen Social-Media-Aufrufe", trends["views"].label, trends["views"].color),
        Kpi("Engagement-Rate", _format_percent(_safe_rate(interactions, views)), "Interaktionen geteilt durch Aufrufe", trends["engagement_rate"].label, trends["engagement_rate"].color),
        Kpi("Gutschein-Nutzungen", _format_number(voucher_uses), "Eingelöste Aktionen und Rabattcodes", trends["voucher_uses"].label, trends["voucher_uses"].color),
        Kpi("Google-Bewertung", f"{latest_rating:.1f}" if latest_rating else "-", "Letzter Durchschnitt über ausgewählte Bereiche", trends["google_rating"].label, trends["google_rating"].color),
    ]


def budget_totals_by_brand(data: MarketingData) -> pd.DataFrame:
    frame = data.budget_categories
    if frame.empty:
        return pd.DataFrame(columns=["brand", "report_year", "planned", "used", "available", "usage_rate"])
    totals = frame[frame["is_total"]].copy()
    totals["usage_rate"] = totals["used"] / totals["planned"].mask(totals["planned"] == 0)
    return totals[["brand", "report_year", "planned", "used", "available", "usage_rate"]]


def social_by_week(data: MarketingData) -> pd.DataFrame:
    frame = data.social
    if frame.empty:
        return pd.DataFrame()
    summary = (
        frame.groupby(["brand", "report_year", "calendar_week"], as_index=False)
        .agg(
            views=("views", "sum"),
            interactions=("interactions", "sum"),
            new_followers=("new_followers", "sum"),
            followers=("followers", "max"),
        )
        .sort_values(["brand", "report_year", "calendar_week"])
    )
    summary["week_label"] = (
        summary["report_year"].astype(int).astype(str)
        + "-KW "
        + summary["calendar_week"].astype(int).astype(str).str.zfill(2)
    )
    summary["engagement_rate"] = summary["interactions"] / summary["views"].replace(0, pd.NA)
    return summary


def acquisition_by_brand(data: MarketingData) -> pd.DataFrame:
    if data.acquisition.empty:
        return pd.DataFrame()
    return (
        data.acquisition.groupby(["brand", "report_year"], as_index=False)
        .agg(
            new_customers=("new_customers", "sum"),
            returning_customers=("returning_customers", "sum"),
            personal_referral=("personal_referral", "sum"),
            events=("events", "sum"),
            search_engine=("search_engine", "sum"),
        )
        .sort_values(["brand", "report_year"])
    )


def latest_operational_snapshot(data: MarketingData) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for brand, frame in data.app.groupby("brand") if not data.app.empty else []:
        latest = frame.sort_values(["report_year", "calendar_week"]).iloc[-1]
        rows.append(
            {
                "brand": brand,
                "metric": "App-Nutzer",
                "value": _format_number(latest.get("app_users", 0)),
                "context": f"KW {int(latest.get('calendar_week')):02d}",
            }
        )
    for brand, frame in data.newsletter.groupby("brand") if not data.newsletter.empty else []:
        latest = frame.sort_values(["report_year", "calendar_week"]).iloc[-1]
        rows.append(
            {
                "brand": brand,
                "metric": "Newsletter Öffnungsrate",
                "value": _format_percent(latest.get("open_rate", 0)),
                "context": str(latest.get("topic", ""))[:80],
            }
        )
    for brand, frame in data.satisfaction.groupby("brand") if not data.satisfaction.empty else []:
        latest = frame.sort_values(["report_year", "calendar_week"]).iloc[-1]
        rows.append(
            {
                "brand": brand,
                "metric": "Google-Bewertung",
                "value": f"{latest.get('google_rating', 0):.1f}",
                "context": f"{int(latest.get('google_reviews_total', 0))} Bewertungen",
            }
        )
    return pd.DataFrame(rows)


def _build_monthly_trends(data: MarketingData) -> dict[str, Trend]:
    return {
        "budget_used": _trend_from_monthly_budget(data.budget_monthly),
        "new_customers": _trend_from_weekly_sum(data.acquisition, "new_customers"),
        "views": _trend_from_weekly_sum(data.social, "views"),
        "engagement_rate": _trend_from_weekly_rate(data.social, "interactions", "views"),
        "voucher_uses": _trend_from_date_or_week(data.retention, "uses", "start_date"),
        "google_rating": _trend_from_weekly_latest_average(data.satisfaction, "google_rating"),
    }


def _trend_from_monthly_budget(frame: pd.DataFrame) -> Trend:
    if frame.empty:
        return _no_comparison()
    totals = frame[(frame["is_total"]) & (frame["metric"] == "Verwendet")].copy()
    if totals.empty:
        return _no_comparison()
    monthly = totals.groupby(["report_year", "month_number"], as_index=False)["amount"].sum()
    return _trend_from_period_values(monthly, "amount")


def _trend_from_weekly_sum(frame: pd.DataFrame, value_column: str) -> Trend:
    if frame.empty or value_column not in frame or not {"report_year", "calendar_week"}.issubset(frame.columns):
        return _no_comparison()
    monthly = _add_month_from_week(frame).groupby(["report_year", "month_number"], as_index=False)[value_column].sum()
    return _trend_from_period_values(monthly, value_column)


def _trend_from_weekly_rate(frame: pd.DataFrame, numerator: str, denominator: str) -> Trend:
    if frame.empty or numerator not in frame or denominator not in frame or not {"report_year", "calendar_week"}.issubset(frame.columns):
        return _no_comparison()
    monthly = (
        _add_month_from_week(frame)
        .groupby(["report_year", "month_number"], as_index=False)
        .agg(numerator=(numerator, "sum"), denominator=(denominator, "sum"))
    )
    monthly["rate"] = monthly["numerator"] / monthly["denominator"].mask(monthly["denominator"] == 0)
    return _trend_from_period_values(monthly, "rate", is_rate=True)


def _trend_from_date_or_week(frame: pd.DataFrame, value_column: str, date_column: str) -> Trend:
    if frame.empty or value_column not in frame:
        return _no_comparison()
    data = frame.copy()
    if date_column in data:
        dates = pd.to_datetime(data[date_column], errors="coerce")
        data["month_number"] = dates.dt.month
        missing_month = data["month_number"].isna()
        if missing_month.any() and {"report_year", "calendar_week"}.issubset(data.columns):
            data.loc[missing_month, "month_number"] = _week_months(data.loc[missing_month])
    elif {"report_year", "calendar_week"}.issubset(data.columns):
        data = _add_month_from_week(data)
    else:
        return _no_comparison()
    monthly = data.dropna(subset=["month_number"]).groupby(["report_year", "month_number"], as_index=False)[value_column].sum()
    return _trend_from_period_values(monthly, value_column)


def _trend_from_weekly_latest_average(frame: pd.DataFrame, value_column: str) -> Trend:
    if frame.empty or value_column not in frame or not {"report_year", "calendar_week"}.issubset(frame.columns):
        return _no_comparison()
    data = _add_month_from_week(frame)
    monthly = (
        data.sort_values(["report_year", "calendar_week"])
        .groupby(["report_year", "month_number", "brand"], as_index=False)
        .tail(1)
        .groupby(["report_year", "month_number"], as_index=False)[value_column]
        .mean()
    )
    return _trend_from_period_values(monthly, value_column, is_rate=True, precision=1)


def _trend_from_period_values(frame: pd.DataFrame, value_column: str, is_rate: bool = False, precision: int = 1) -> Trend:
    data = frame.dropna(subset=["report_year", "month_number", value_column]).copy()
    if data.empty:
        return _no_comparison()
    data["period"] = data["report_year"].astype(int) * 12 + data["month_number"].astype(int)
    data = data.sort_values("period")
    latest = data.iloc[-1]
    previous_rows = data[data["period"] == latest["period"] - 1]
    if previous_rows.empty:
        return _no_comparison()

    current_value = float(latest[value_column])
    previous_value = float(previous_rows.iloc[-1][value_column])
    if previous_value == 0:
        if current_value == 0:
            return Trend("→ 0,0 %", "off")
        return Trend("▲ neuer Wert", "normal")

    change = (current_value - previous_value) / abs(previous_value)
    if abs(change) < 0.001:
        return Trend("→ 0,0 %", "off")

    arrow = "▲" if change > 0 else "▼"
    color = "normal" if change > 0 else "inverse"
    if is_rate:
        points = current_value - previous_value
        return Trend(f"{arrow} {points * 100:.{precision}f} Pp.".replace(".", ","), color)
    return Trend(f"{arrow} {change:.1%}".replace(".", ","), color)


def _add_month_from_week(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["month_number"] = _week_months(data)
    return data


def _week_months(frame: pd.DataFrame) -> pd.Series:
    months = []
    for row in frame.itertuples(index=False):
        year = int(getattr(row, "report_year"))
        week = int(getattr(row, "calendar_week"))
        months.append(date.fromisocalendar(year, week, 1).month)
    return pd.Series(months, index=frame.index, dtype="float64")


def _no_comparison() -> Trend:
    return Trend("○ kein Vormonat", "off")


def _budget_total(frame: pd.DataFrame) -> dict[str, float]:
    totals = frame[frame["is_total"]] if not frame.empty else pd.DataFrame()
    return {
        "planned": _sum(totals, "planned"),
        "used": _sum(totals, "used"),
        "available": _sum(totals, "available"),
    }


def _sum(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame:
        return 0.0
    return float(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())


def _latest_average(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame:
        return 0.0
    latest = frame.sort_values(["report_year", "calendar_week"]).groupby("brand").tail(1)
    return float(pd.to_numeric(latest[column], errors="coerce").dropna().mean())


def _safe_rate(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def _format_percent(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")


def _format_currency(value: float) -> str:
    return f"{value:,.0f} EUR".replace(",", ".")
