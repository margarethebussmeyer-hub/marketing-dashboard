from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DashboardConfig


class DataValidationError(ValueError):
    """Raised when the Excel input cannot be processed safely."""


def validate_workbook_path(path: Path) -> None:
    """Validate that the configured Excel workbook exists and looks usable."""

    if not path.exists():
        raise DataValidationError(
            f"Die Exceldatei wurde nicht gefunden: {path}. "
            "Bitte lege die Datei in data/input/ ab oder lade sie im Dashboard hoch."
        )
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise DataValidationError(
            f"Die Datei '{path.name}' ist keine unterstützte Exceldatei. "
            "Erwartet wird eine .xlsx- oder .xlsm-Datei."
        )


def validate_sheet_names(available_sheets: list[str], config: DashboardConfig) -> None:
    """Ensure the workbook contains the expected marketing worksheets."""

    missing = [sheet for sheet in config.expected_sheet_names if sheet not in available_sheets]
    if missing:
        raise DataValidationError(
            "Folgende Tabellenblätter fehlen: "
            f"{', '.join(missing)}. Vorhandene Blätter: {', '.join(available_sheets)}."
        )


def validate_required_columns(frame: pd.DataFrame, sheet_name: str) -> None:
    """Check columns needed for the dashboard's core KPIs."""

    required = {"calendar_week", "new_followers", "interactions", "views"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise DataValidationError(
            f"Im Tabellenblatt '{sheet_name}' fehlen Pflichtspalten: {', '.join(missing)}. "
            "Erwartet werden mindestens KW, Neue Follower, Interaktionen und Aufrufe."
        )


def validate_calendar_weeks(frame: pd.DataFrame, config: DashboardConfig, sheet_name: str) -> None:
    """Validate week values after numeric conversion."""

    invalid = frame[
        frame["calendar_week"].isna()
        | (frame["calendar_week"] < config.min_week)
        | (frame["calendar_week"] > config.max_week)
    ]
    if not invalid.empty:
        rows = ", ".join(str(index + 3) for index in invalid.index[:5])
        raise DataValidationError(
            f"Im Tabellenblatt '{sheet_name}' sind ungültige Kalenderwochen in Excel-Zeile(n) {rows}. "
            f"Erwartet werden Werte von {config.min_week} bis {config.max_week}."
        )
