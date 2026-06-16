from __future__ import annotations

import hmac
import os
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.charts import (
    acquisition_chart,
    budget_category_chart,
    budget_monthly_usage_chart,
    budget_usage_chart,
    social_line_chart,
    voucher_usage_chart,
)
from src.config import DashboardConfig
from src.data_loader import load_dashboard_data
from src.data_processing import (
    available_brands,
    available_years,
    build_discount_code_overview,
    filter_dashboard_data,
    top_booking_suppliers,
)
from src.data_validation import DataValidationError
from src.metrics import (
    acquisition_by_brand,
    budget_totals_by_brand,
    build_executive_kpis,
    latest_operational_snapshot,
    social_by_week,
)
from src.styles import dashboard_css


st.set_page_config(page_title="Marketing-Dashboard", page_icon="M", layout="wide")


COLUMN_LABELS = {
    "brand": "Bereich",
    "report_year": "Jahr",
    "calendar_week": "KW",
    "week_label": "Woche",
    "metric": "Kennzahl",
    "value": "Wert",
    "context": "Kontext",
    "planned": "Geplant",
    "used": "Verwendet",
    "available": "Verfügbar",
    "usage_rate": "Verbrauchsquote",
    "category": "Kategorie",
    "is_total": "Summenzeile",
    "supplier": "Lieferant",
    "amount": "Betrag",
    "date": "Datum",
    "month": "Monat",
    "description": "Buchungstext",
    "document": "Beleg",
    "new_customers": "Neukunden",
    "returning_customers": "Wiedereinsteiger",
    "personal_referral": "Persönliche Empfehlung",
    "events": "Veranstaltungen",
    "other": "Sonstiges",
    "search_engine": "Suchmaschine",
    "brand_code": "Unternehmen",
    "campaign": "Aktion",
    "voucher_value": "Gutscheinwert",
    "voucher_name": "Gutscheinname",
    "discount_code": "Rabattcode",
    "uses": "Nutzungen",
    "channel": "Kanal",
    "period": "Zeitraum",
    "start_date": "Start",
    "end_date": "Ende",
    "existing_customers": "Bestandskunden",
    "platform": "Plattform",
    "followers": "Follower",
    "new_followers": "Neue Follower",
    "interactions": "Interaktionen",
    "views": "Aufrufe",
    "profile_views": "Profilaufrufe",
    "post_count": "Beiträge Anzahl",
    "reel_count": "Reels Anzahl",
    "story_count": "Storys Anzahl",
    "cooperations": "Kooperationen",
    "post_reach": "Beiträge Reichweite",
    "post_likes": "Beiträge Gefällt mir",
    "post_comments": "Beiträge Kommentare",
    "post_saves": "Beiträge Gespeichert",
    "post_reposts": "Beiträge Reposts",
    "reel_reach": "Reels Reichweite",
    "reel_likes": "Reels Gefällt mir",
    "reel_comments": "Reels Kommentare",
    "reel_saves": "Reels Gespeichert",
    "reel_reposts": "Reels Reposts",
    "engagement_rate": "Engagement-Rate",
    "app_users": "App-Nutzer",
    "app_downloads": "App-Downloads",
    "push_recipients": "Push-Empfänger",
    "push_click_rate": "Push-Klickrate",
    "opened_notifications": "Geöffnete Benachrichtigungen",
    "push_message": "Push-Nachricht",
    "sent_at": "Versanddatum",
    "topic": "Thema",
    "audience": "Zielgruppe",
    "recipients": "Empfängerzahl",
    "open_rate": "Öffnungsrate",
    "click_rate": "Klickrate",
    "unsubscribe_rate": "Abmeldungen",
    "new_google_reviews": "Neue Google-Bewertungen",
    "google_rating": "Google-Durchschnittsbewertung",
    "google_reviews_total": "Google-Bewertungen gesamt",
}


@st.cache_data(show_spinner=False)
def _load_data(marketing_source, budget_source):
    return load_dashboard_data(marketing_source, budget_source)


@st.cache_data(show_spinner=False)
def _load_data_from_paths(marketing_path: str, budget_path: str):
    return load_dashboard_data(Path(marketing_path), Path(budget_path))


def main() -> None:
    st.markdown(dashboard_css(), unsafe_allow_html=True)
    _require_password()
    config = DashboardConfig()
    _render_header()
    marketing_source, budget_source = _render_uploads(config)
    _stop_if_required_sources_are_missing(marketing_source, budget_source)

    try:
        if isinstance(marketing_source, Path) and isinstance(budget_source, Path):
            data = _load_data_from_paths(str(marketing_source), str(budget_source))
        else:
            data = _load_data(marketing_source, budget_source)
    except DataValidationError as error:
        st.error(str(error))
        st.stop()
    except Exception as error:
        st.error(f"Die Exceldateien konnten nicht geladen werden. Technischer Hinweis: {error}")
        st.stop()

    filtered = _render_filters(data)
    _render_kpis(filtered)

    overview_tab, social_tab, budget_tab, actions_tab, operations_tab, raw_tab = st.tabs(
        ["Überblick", "Social Media", "Budget", "Aktionen", "Newsletter/App", "Daten"]
    )

    with overview_tab:
        _render_overview(filtered)
    with social_tab:
        _render_social(filtered)
    with budget_tab:
        _render_budget(filtered)
    with actions_tab:
        _render_actions(filtered)
    with operations_tab:
        _render_operations(filtered)
    with raw_tab:
        _render_raw_tables(filtered)


def _render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Marketing Performance</div>
            <div class="hero-title">Dashboard für Budget, Wachstum und Wirkung</div>
            <div class="hero-copy">
                Die wichtigsten Marketingdaten aus Kennzahlen- und Budgetdatei: Budgetverbrauch,
                Neukundengewinnung, Social-Media-Wirkung, Aktionen, App, Newsletter und Bewertungen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _require_password() -> None:
    configured_password = _configured_password()
    if not configured_password:
        return

    if st.session_state.get("authenticated"):
        return

    st.title("Geschütztes Marketing-Dashboard")
    password = st.text_input("Passwort", type="password")
    if st.button("Anmelden", type="primary"):
        if hmac.compare_digest(password, configured_password):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Das Passwort ist nicht korrekt.")
    st.stop()


def _configured_password() -> str:
    try:
        secret_password = st.secrets.get("DASHBOARD_PASSWORD", "")
    except Exception:
        secret_password = ""
    return os.getenv("DASHBOARD_PASSWORD", secret_password)


def _render_filters(data):
    st.sidebar.header("Filter")
    brands = available_brands(data)
    years = available_years(data)
    selected_brands = st.sidebar.multiselect("Bereich", options=brands, default=brands)
    selected_years = st.sidebar.multiselect("Jahr", options=years, default=years)
    if not selected_brands or not selected_years:
        st.warning("Bitte mindestens einen Bereich und ein Jahr auswählen.")
        st.stop()
    return filter_dashboard_data(data, selected_brands, selected_years)


def _render_uploads(config: DashboardConfig):
    st.sidebar.header("Datenquellen")
    marketing_upload = st.sidebar.file_uploader(
        "Wöchentliche Kennzahlen hochladen",
        type=["xlsx", "xlsm"],
        help="Erwartete Datei: Kennzahlen-Marketing.xlsx",
        key="marketing_upload",
    )
    budget_upload = st.sidebar.file_uploader(
        "Budgetbericht hochladen",
        type=["xlsx", "xlsm"],
        help="Erwartete Datei: 2026_2025_Marketing_Budget.xlsx",
        key="budget_upload",
    )

    if marketing_upload is None:
        st.sidebar.caption(f"Kennzahlen: Standarddatei {config.marketing_path.name}")
    else:
        st.sidebar.caption(f"Kennzahlen: Upload {marketing_upload.name}")

    if budget_upload is None:
        st.sidebar.caption(f"Budget: Standarddatei {config.budget_path.name}")
    else:
        st.sidebar.caption(f"Budget: Upload {budget_upload.name}")

    return (
        marketing_upload if marketing_upload is not None else config.marketing_path,
        budget_upload if budget_upload is not None else config.budget_path,
    )


def _stop_if_required_sources_are_missing(marketing_source, budget_source) -> None:
    missing = []
    if isinstance(marketing_source, Path) and not marketing_source.exists():
        missing.append("wöchentliche Kennzahlen")
    if isinstance(budget_source, Path) and not budget_source.exists():
        missing.append("Budgetbericht")
    if missing:
        st.info(
            "Bitte lade links unter Datenquellen folgende Datei(en) hoch: "
            + ", ".join(missing)
            + "."
        )
        st.stop()


def _render_kpis(data) -> None:
    kpis = build_executive_kpis(data)
    columns = st.columns(len(kpis))
    for column, kpi in zip(columns, kpis):
        column.metric(kpi.label, kpi.value, delta=kpi.delta, delta_color=kpi.delta_color, help=kpi.help_text)


def _render_overview(data) -> None:
    left, right = st.columns(2)
    with left:
        budget = budget_totals_by_brand(data)
        if not budget.empty:
            st.plotly_chart(budget_usage_chart(budget), width="stretch", key="overview_budget_usage")
    with right:
        acquisition = acquisition_by_brand(data)
        if not acquisition.empty:
            st.plotly_chart(acquisition_chart(acquisition), width="stretch", key="overview_acquisition")

    st.subheader("Operative Signale")
    snapshot = latest_operational_snapshot(data)
    if snapshot.empty:
        st.info("Keine operativen Daten für die aktuelle Auswahl vorhanden.")
    else:
        _render_dataframe(snapshot)


def _render_social(data) -> None:
    weekly = social_by_week(data)
    if weekly.empty:
        st.info("Keine Social-Media-Daten für die aktuelle Auswahl vorhanden.")
        return

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            social_line_chart(weekly, "views", "Social-Media-Aufrufe", "Aufrufe"),
            width="stretch",
            key="social_views",
        )
    with right:
        st.plotly_chart(
            social_line_chart(weekly, "interactions", "Social-Media-Interaktionen", "Interaktionen"),
            width="stretch",
            key="social_interactions",
        )

    _render_dataframe(
        weekly[["brand", "report_year", "calendar_week", "followers", "new_followers", "views", "interactions", "engagement_rate"]],
    )


def _render_budget(data) -> None:
    totals = budget_totals_by_brand(data)
    if totals.empty:
        st.info("Keine Budgetdaten für die aktuelle Auswahl vorhanden.")
        return

    st.plotly_chart(budget_usage_chart(totals), width="stretch", key="budget_usage")
    st.plotly_chart(budget_monthly_usage_chart(data.budget_monthly), width="stretch", key="budget_monthly_usage")
    st.plotly_chart(budget_category_chart(data.budget_categories), width="stretch", key="budget_categories")

    left, right = st.columns(2)
    with left:
        st.subheader("Budget nach Bereich")
        _render_dataframe(
            totals,
            currency_columns={"planned", "used", "available"},
            percent_columns={"usage_rate"},
        )
    with right:
        st.subheader("Größte Lieferanten")
        _render_dataframe(top_booking_suppliers(data.bookings), currency_columns={"amount"})


def _render_actions(data) -> None:
    codes = build_discount_code_overview(data.retention)
    if codes.empty:
        st.info("Keine Aktionen oder Rabattcodes für die aktuelle Auswahl vorhanden.")
        return

    st.plotly_chart(voucher_usage_chart(codes), width="stretch", key="voucher_usage")
    st.subheader("Rabattcodes und Aktionen")
    for (brand, year), group in codes.groupby(["brand", "report_year"], sort=True):
        with st.expander(f"{brand} · {int(year)}", expanded=True):
            for row in group.itertuples(index=False):
                channel = f" · {row.channel}" if row.channel else ""
                period = f" · Start: {row.period}" if row.period else ""
                st.markdown(f"- **{row.discount_code}**: {_format_int(row.uses)} Nutzungen{channel}{period}")


def _render_operations(data) -> None:
    left, right = st.columns(2)
    with left:
        st.subheader("Newsletter")
        if data.newsletter.empty:
            st.info("Keine Newsletter-Daten vorhanden.")
        else:
            _render_dataframe(data.newsletter)
    with right:
        st.subheader("App")
        if data.app.empty:
            st.info("Keine App-Daten vorhanden.")
        else:
            _render_dataframe(data.app)

    st.subheader("Kundenzufriedenheit")
    if data.satisfaction.empty:
        st.info("Keine Bewertungsdaten vorhanden.")
    else:
        _render_dataframe(data.satisfaction)


def _render_raw_tables(data) -> None:
    tables = {
        "Neukundengewinnung": data.acquisition,
        "Kundenbindung": data.retention,
        "Social Media": data.social,
        "Budget Kategorien": data.budget_categories,
        "Buchungsliste": data.bookings,
    }
    for label, frame in tables.items():
        with st.expander(label):
            _render_dataframe(frame)


def _render_dataframe(frame, currency_columns: set[str] | None = None, percent_columns: set[str] | None = None) -> None:
    display_frame = frame.copy()
    for column in currency_columns or set():
        if column in display_frame.columns:
            display_frame[column] = display_frame[column].map(_format_currency)
    for column in percent_columns or set():
        if column in display_frame.columns:
            display_frame[column] = display_frame[column].map(_format_percent)
    renamed = display_frame.rename(columns={column: COLUMN_LABELS.get(column, column) for column in display_frame.columns})
    st.dataframe(renamed, width="stretch", hide_index=True)


def _format_int(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def _format_currency(value: float) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_percent(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")


if __name__ == "__main__":
    main()
