from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


BRAND_COLORS = {
    "Gemüsegärtner": "#4f7f3b",
    "Weidenhof": "#d97732",
}


def budget_usage_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        frame,
        x="brand",
        y=["used", "available"],
        color_discrete_map={"used": "#d97732", "available": "#779d45"},
        labels={"brand": "Bereich", "value": "Budget in EUR", "variable": ""},
        title="Budget: verwendet vs. verfügbar",
        facet_col="report_year" if frame["report_year"].nunique() > 1 else None,
    )
    figure.for_each_trace(lambda trace: trace.update(name={"used": "Verwendet", "available": "Verfügbar"}.get(trace.name, trace.name)))
    return _style_figure(figure)


def budget_category_chart(frame: pd.DataFrame) -> go.Figure:
    categories = frame[~frame["is_total"]].copy()
    figure = px.bar(
        categories,
        x="category",
        y="used",
        color="brand",
        color_discrete_map=BRAND_COLORS,
        labels={"category": "Kategorie", "used": "Verwendet in EUR", "brand": "Bereich"},
        title="Budgetverbrauch nach Kategorie",
        barmode="group",
    )
    return _style_figure(figure)


def budget_monthly_usage_chart(frame: pd.DataFrame) -> go.Figure:
    """Show planned and used budget per month."""

    if frame.empty:
        return _style_figure(go.Figure())

    totals = frame[frame["is_total"]].copy()
    totals = totals[totals["metric"].isin(["Geplant", "Verwendet"])]
    monthly = (
        totals.groupby(["brand", "report_year", "month_number", "month", "metric"], as_index=False)["amount"]
        .sum()
        .sort_values(["report_year", "month_number", "brand", "metric"])
    )
    monthly["month_label"] = (
        monthly["report_year"].astype(int).astype(str)
        + " "
        + monthly["month"].astype(str)
    )

    figure = px.bar(
        monthly,
        x="month_label",
        y="amount",
        color="metric",
        facet_row="brand" if monthly["brand"].nunique() > 1 else None,
        barmode="group",
        color_discrete_map={"Geplant": "#779d45", "Verwendet": "#d97732"},
        labels={"month_label": "Monat", "amount": "Budget in EUR", "metric": ""},
        title="Monatlicher Budgetverbrauch: geplant vs. verwendet",
    )
    return _style_figure(figure)


def social_line_chart(frame: pd.DataFrame, y_column: str, title: str, y_title: str) -> go.Figure:
    figure = px.line(
        frame,
        x="week_label",
        y=y_column,
        color="brand",
        markers=True,
        color_discrete_map=BRAND_COLORS,
        labels={"week_label": "Woche", y_column: y_title, "brand": "Bereich"},
        title=title,
    )
    return _style_figure(figure)


def acquisition_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        frame,
        x="brand",
        y="new_customers",
        color="report_year",
        labels={"brand": "Bereich", "new_customers": "Neukunden", "report_year": "Jahr"},
        title="Neukunden nach Bereich und Jahr",
        barmode="group",
    )
    return _style_figure(figure)


def voucher_usage_chart(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _style_figure(go.Figure())
    figure = px.bar(
        frame,
        x="discount_code",
        y="uses",
        color="brand",
        color_discrete_map=BRAND_COLORS,
        labels={"discount_code": "Code", "uses": "Nutzungen", "brand": "Bereich"},
        title="Gutschein- und Rabattcode-Nutzungen",
    )
    return _style_figure(figure)


def _style_figure(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fffaf0",
        font={"family": "Arial, sans-serif", "color": "#26351f"},
        title={"font": {"size": 20, "color": "#26351f"}},
        legend_title_text="",
        margin={"l": 20, "r": 20, "t": 60, "b": 35},
    )
    figure.update_xaxes(showgrid=False, zeroline=False, tickangle=-25)
    figure.update_yaxes(gridcolor="#eadcc4", zeroline=False)
    return figure
