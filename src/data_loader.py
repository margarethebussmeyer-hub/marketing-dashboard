from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.config import (
    BRAND_ALIASES,
    BRAND_GG,
    BRAND_WH,
    EXPECTED_BUDGET_SHEETS,
    EXPECTED_MARKETING_SHEETS,
    MONTH_ORDER,
)
from src.data_validation import DataValidationError, validate_workbook_path


@dataclass(frozen=True)
class MarketingData:
    acquisition: pd.DataFrame
    retention: pd.DataFrame
    app: pd.DataFrame
    newsletter: pd.DataFrame
    satisfaction: pd.DataFrame
    social: pd.DataFrame
    budget_categories: pd.DataFrame
    budget_monthly: pd.DataFrame
    bookings: pd.DataFrame


def load_dashboard_data(marketing_path: Path, budget_path: Path) -> MarketingData:
    """Load all dashboard inputs from the restructured marketing and budget workbooks."""

    validate_workbook_path(marketing_path)
    validate_workbook_path(budget_path)

    marketing_excel = pd.ExcelFile(marketing_path, engine="openpyxl")
    budget_excel = pd.ExcelFile(budget_path, engine="openpyxl")
    _validate_sheets(marketing_excel.sheet_names, EXPECTED_MARKETING_SHEETS, marketing_path.name)
    _validate_sheets(budget_excel.sheet_names, EXPECTED_BUDGET_SHEETS, budget_path.name)

    return MarketingData(
        acquisition=_load_acquisition(marketing_excel),
        retention=_load_retention(marketing_excel),
        app=_load_app(marketing_excel),
        newsletter=_load_newsletter(marketing_excel),
        satisfaction=_load_satisfaction(marketing_excel),
        social=_load_social(marketing_excel),
        budget_categories=_load_budget_categories(budget_excel),
        budget_monthly=_load_budget_monthly(budget_excel),
        bookings=_load_bookings(budget_excel),
    )


def normalize_brand(value: object, default: str | None = None) -> str:
    """Normalize workbook brand codes such as WH, GG and GGBE."""

    if pd.isna(value) or str(value).strip() == "":
        if default is None:
            raise DataValidationError("Ein Unternehmenskennzeichen fehlt und es gibt keinen sinnvollen Standardwert.")
        return default

    key = str(value).strip().upper()
    if key not in BRAND_ALIASES:
        raise DataValidationError(
            f"Unbekanntes Unternehmenskennzeichen '{value}'. Erwartet werden WH, GG oder GGBE."
        )
    return BRAND_ALIASES[key]


def _validate_sheets(available: list[str], expected: tuple[str, ...], workbook_name: str) -> None:
    missing = [sheet for sheet in expected if sheet not in available]
    if missing:
        raise DataValidationError(
            f"In '{workbook_name}' fehlen Tabellenblätter: {', '.join(missing)}. "
            f"Vorhanden: {', '.join(available)}."
        )


def _load_acquisition(excel: pd.ExcelFile) -> pd.DataFrame:
    frame = _read_clean_sheet(excel, "Neukundengewinnung")
    frame = frame.rename(
        columns={
            "kw": "calendar_week",
            "jahr": "report_year",
            "anzahl_neukunden_gesamt": "new_customers",
            "personliche_empfehlung": "personal_referral",
            "veranstaltungen": "events",
            "sonstiges": "other",
            "suchmaschine": "search_engine",
            "wiedereinsteiger": "returning_customers",
            "unternehmen_wh_ggbe": "brand_code",
        }
    )
    frame = _keep_columns(
        frame,
        [
            "calendar_week",
            "report_year",
            "new_customers",
            "personal_referral",
            "events",
            "other",
            "search_engine",
            "returning_customers",
            "brand_code",
        ],
    )
    frame = frame.dropna(subset=["calendar_week", "report_year", "brand_code"]).copy()
    frame["brand"] = frame["brand_code"].map(normalize_brand)
    return _coerce_numeric(frame, exclude={"brand", "brand_code"})


def _load_retention(excel: pd.ExcelFile) -> pd.DataFrame:
    frame = _read_clean_sheet(excel, "Kundenbindung")
    frame = frame.rename(
        columns={
            "kw": "calendar_week",
            "aktion": "campaign",
            "gutscheinwert": "voucher_value",
            "gutscheinname": "voucher_name",
            "start": "start_date",
            "ende": "end_date",
            "anzahl_nutzungen": "uses",
            "kanal": "channel",
            "neukunden": "new_customers",
            "bestandskunden": "existing_customers",
            "unternehmen_wh_ggbe": "brand_code",
        }
    )
    frame = _keep_columns(
        frame,
        [
            "calendar_week",
            "campaign",
            "voucher_value",
            "voucher_name",
            "start_date",
            "end_date",
            "uses",
            "channel",
            "new_customers",
            "existing_customers",
            "brand_code",
        ],
    )
    frame = frame.dropna(subset=["voucher_name", "brand_code"], how="any").copy()
    frame["brand"] = frame["brand_code"].map(normalize_brand)
    frame["start_date"] = pd.to_datetime(frame["start_date"], errors="coerce")
    frame["end_date"] = pd.to_datetime(frame["end_date"], errors="coerce")
    frame["report_year"] = frame["start_date"].dt.year
    frame.loc[frame["report_year"].isna(), "report_year"] = 2026
    return _coerce_numeric(frame, exclude={"brand", "brand_code", "campaign", "voucher_name", "channel", "start_date", "end_date"})


def _load_app(excel: pd.ExcelFile) -> pd.DataFrame:
    frame = _read_clean_sheet(excel, "App")
    frame = frame.rename(
        columns={
            "kw": "calendar_week",
            "nutzer": "app_users",
            "app_downloads_woche": "app_downloads",
            "push_nachrichten_empfanger": "push_recipients",
            "push_klickrate": "push_click_rate",
            "geoffnete_benachrichtigungen": "opened_notifications",
            "push_nachricht": "push_message",
            "unternehmen_wh_ggbe": "brand_code",
        }
    )
    frame = _keep_columns(
        frame,
        [
            "calendar_week",
            "app_users",
            "app_downloads",
            "push_recipients",
            "push_click_rate",
            "opened_notifications",
            "push_message",
            "brand_code",
        ],
    )
    frame = frame.dropna(subset=["calendar_week", "brand_code"]).copy()
    frame["brand"] = frame["brand_code"].map(normalize_brand)
    frame["report_year"] = 2026
    return _coerce_numeric(frame, exclude={"brand", "brand_code", "push_message"})


def _load_newsletter(excel: pd.ExcelFile) -> pd.DataFrame:
    frame = _read_clean_sheet(excel, "Newsletter")
    frame = frame.rename(
        columns={
            "kw": "calendar_week",
            "versanddatum": "sent_at",
            "thema": "topic",
            "zielgruppe": "audience",
            "empfangerzahl": "recipients",
            "offnungsrate": "open_rate",
            "klickrate": "click_rate",
            "abmeldungen": "unsubscribe_rate",
            "unternehmen_wh_ggbe": "brand_code",
        }
    )
    frame = _keep_columns(
        frame,
        [
            "calendar_week",
            "sent_at",
            "topic",
            "audience",
            "recipients",
            "open_rate",
            "click_rate",
            "unsubscribe_rate",
            "brand_code",
        ],
    )
    frame = frame.dropna(subset=["calendar_week"]).copy()
    frame["brand"] = frame["brand_code"].map(lambda value: normalize_brand(value, default=BRAND_GG))
    frame["report_year"] = 2026
    return _coerce_numeric(frame, exclude={"brand", "brand_code", "sent_at", "topic", "audience"})


def _load_satisfaction(excel: pd.ExcelFile) -> pd.DataFrame:
    frame = _read_clean_sheet(excel, "Kundenzufriedenheit")
    frame = frame.rename(
        columns={
            "kw": "calendar_week",
            "jahr": "report_year",
            "neue_google_bewertungen": "new_google_reviews",
            "durchschnittsbewertung_google": "google_rating",
            "anzahl_bewertungen_gesamt": "google_reviews_total",
        }
    )
    frame = _keep_columns(
        frame,
        ["calendar_week", "report_year", "new_google_reviews", "google_rating", "google_reviews_total"],
    )
    frame = frame.dropna(subset=["calendar_week", "report_year", "google_reviews_total"]).copy()
    frame = _coerce_numeric(frame)
    # The sheet has no brand column. Review totals make the mapping explicit enough for the current workbook.
    frame["brand"] = frame["google_reviews_total"].map(lambda value: BRAND_WH if value < 150 else BRAND_GG)
    return frame


def _load_social(excel: pd.ExcelFile) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for sheet_name, brand in (("Social Media-GG", BRAND_GG), ("Social Media-WH", BRAND_WH)):
        frame = _read_clean_sheet(excel, sheet_name)
        frame = frame.rename(
            columns={
                "kw": "calendar_week",
                "jahr": "report_year",
                "plattform": "platform",
                "follower": "followers",
                "neue_follower": "new_followers",
                "interaktionen": "interactions",
                "aufrufe": "views",
                "profilaufrufe": "profile_views",
                "beitrage_anzahl": "post_count",
                "reels_anzahl": "reel_count",
                "storys_anzahl": "story_count",
                "kooperationen": "cooperations",
                "beitrage_reichweite": "post_reach",
                "beitrage_gefallt_mir": "post_likes",
                "beitrage_kommentare": "post_comments",
                "beitrage_gespeichert": "post_saves",
                "beitrage_reposts": "post_reposts",
                "reels_reichweite": "reel_reach",
                "reels_gefallt_mir": "reel_likes",
                "reels_kommentare": "reel_comments",
                "reels_gespeichert": "reel_saves",
                "reels_reposts": "reel_reposts",
            }
        )
        frame["brand"] = brand
        frames.append(frame)
    social = pd.concat(frames, ignore_index=True)
    social = _coerce_numeric(social, exclude={"brand", "platform"})
    return social


def _load_budget_categories(excel: pd.ExcelFile) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    frames.append(_parse_budget_section(pd.read_excel(excel, "GGBE_2026_Jahresbudget", header=None, dtype=object), 0, BRAND_GG, 2026)[0])
    frames.append(_parse_budget_section(pd.read_excel(excel, "WH_2026_Jahresbudget", header=None, dtype=object), 0, BRAND_WH, 2026)[0])
    raw_2025 = pd.read_excel(excel, "2025_Jahresbudget", header=None, dtype=object)
    frames.append(_parse_budget_section(raw_2025, 0, BRAND_GG, 2025)[0])
    frames.append(_parse_budget_section(raw_2025, 13, BRAND_WH, 2025)[0])
    return pd.concat(frames, ignore_index=True)


def _load_budget_monthly(excel: pd.ExcelFile) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    frames.append(_parse_budget_section(pd.read_excel(excel, "GGBE_2026_Jahresbudget", header=None, dtype=object), 0, BRAND_GG, 2026)[1])
    frames.append(_parse_budget_section(pd.read_excel(excel, "WH_2026_Jahresbudget", header=None, dtype=object), 0, BRAND_WH, 2026)[1])
    raw_2025 = pd.read_excel(excel, "2025_Jahresbudget", header=None, dtype=object)
    frames.append(_parse_budget_section(raw_2025, 0, BRAND_GG, 2025)[1])
    frames.append(_parse_budget_section(raw_2025, 13, BRAND_WH, 2025)[1])
    return pd.concat(frames, ignore_index=True)


def _load_bookings(excel: pd.ExcelFile) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for sheet_name, brand in (("GGBE_Buchungsliste", BRAND_GG), ("WH_Buchungsliste", BRAND_WH)):
        if sheet_name not in excel.sheet_names:
            continue
        frame = _read_clean_sheet(excel, sheet_name)
        frame = frame.rename(
            columns={
                "datum": "date",
                "monat": "month",
                "jahr": "report_year",
                "lieferant": "supplier",
                "kategorie": "category",
                "buchungstext": "description",
                "beleg1": "document",
                "betrag": "amount",
            }
        )
        frame = _keep_columns(
            frame,
            ["date", "month", "report_year", "supplier", "category", "description", "document", "amount"],
        )
        frame["brand"] = brand
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce", dayfirst=True)
        if "month" in frame.columns:
            frame["month"] = frame["month"].map(_normalize_month_label)
        for column in ("supplier", "category", "description", "document"):
            if column in frame.columns:
                frame[column] = frame[column].map(_normalize_text)
        frame = _coerce_numeric(frame, exclude={"brand", "date", "month", "supplier", "category", "description", "document"})
        frames.append(frame.dropna(subset=["amount"]))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _parse_budget_section(
    raw: pd.DataFrame,
    header_row: int,
    brand: str,
    year: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    month_row = raw.iloc[header_row].ffill()
    metric_row = raw.iloc[header_row + 1]
    category_rows = raw.iloc[header_row + 2 :].copy()

    categories: list[dict[str, object]] = []
    monthly: list[dict[str, object]] = []
    total_cols = {
        str(metric_row[col]).strip(): col
        for col in raw.columns
        if str(month_row[col]).strip().upper() == "SUMME"
    }

    for _, row in category_rows.iterrows():
        category = row.iloc[0]
        if pd.isna(category) or str(category).strip() == "":
            break
        category_name = str(category).strip()
        planned = _to_number(row.get(total_cols.get("Geplant"))) if "Geplant" in total_cols else pd.NA
        used = _to_number(row.get(total_cols.get("Verwendet"))) if "Verwendet" in total_cols else pd.NA
        available = _to_number(row.get(total_cols.get("Verfügbar"))) if "Verfügbar" in total_cols else pd.NA

        categories.append(
            {
                "brand": brand,
                "report_year": year,
                "category": category_name,
                "planned": planned,
                "used": used,
                "available": available,
                "is_total": category_name.upper() == "SUMME",
            }
        )

        for col in raw.columns[1:]:
            month = str(month_row[col]).strip()
            metric = str(metric_row[col]).strip()
            if month not in MONTH_ORDER or metric not in {"Geplant", "Verwendet", "Verfügbar"}:
                continue
            monthly.append(
                {
                    "brand": brand,
                    "report_year": year,
                    "category": category_name,
                    "month": month,
                    "month_number": MONTH_ORDER[month],
                    "metric": metric,
                    "amount": _to_number(row.get(col)),
                    "is_total": category_name.upper() == "SUMME",
                }
            )

        if category_name.upper() == "SUMME":
            break

    category_frame = pd.DataFrame(categories)
    monthly_frame = pd.DataFrame(monthly)
    for frame, columns in ((category_frame, ["planned", "used", "available"]), (monthly_frame, ["amount"])):
        for column in columns:
            if column in frame:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return category_frame, monthly_frame


def _read_clean_sheet(excel: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    frame = pd.read_excel(excel, sheet_name=sheet_name, header=0, dtype=object)
    frame = frame.dropna(how="all").copy()
    frame.columns = [_slugify(column) for column in frame.columns]
    frame = frame.loc[:, ~frame.columns.str.startswith("unnamed")]
    return frame.reset_index(drop=True)


def _keep_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    existing = [column for column in columns if column in frame.columns]
    return frame[existing].copy()


def _coerce_numeric(frame: pd.DataFrame, exclude: set[str] | None = None) -> pd.DataFrame:
    result = frame.copy()
    excluded = exclude or set()
    for column in result.columns:
        if column in excluded:
            continue
        result[column] = result[column].map(_to_number)
    return result


def _to_number(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    if text in {"", "/", "-", "keiner", "kein aktueller Code"}:
        return pd.NA
    match = re.search(r"-?\d+(?:[.,]\d+)?(?:\.\d{3})*", text)
    if not match:
        return pd.NA
    number = match.group(0)
    if "." in number and "," not in number:
        number = number.replace(".", "") if re.search(r"\.\d{3}$", number) else number
    return float(number.replace(",", "."))


def _normalize_month_label(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (int, float)):
        return f"{int(value):02d}"
    return str(value).strip()


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _slugify(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text.lower())).strip("_")
