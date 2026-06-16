from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MARKETING_PATH = PROJECT_ROOT / "data" / "input" / "Kennzahlen-Marketing.xlsx"
DEFAULT_BUDGET_PATH = PROJECT_ROOT / "data" / "input" / "2026_2025_Marketing_Budget.xlsx"


BRAND_GG = "Gemüsegärtner"
BRAND_WH = "Weidenhof"


@dataclass(frozen=True)
class DashboardConfig:
    marketing_path: Path = DEFAULT_MARKETING_PATH
    budget_path: Path = DEFAULT_BUDGET_PATH


MONTH_ORDER = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}


BRAND_ALIASES = {
    "GG": BRAND_GG,
    "GGBE": BRAND_GG,
    "GEMÜSEGÄRTNER": BRAND_GG,
    "GEMUESEGAERTNER": BRAND_GG,
    "WH": BRAND_WH,
    "WEIDENHOF": BRAND_WH,
}


EXPECTED_MARKETING_SHEETS = (
    "Neukundengewinnung",
    "Kundenbindung",
    "App",
    "Newsletter",
    "Kundenzufriedenheit",
    "Social Media-GG",
    "Social Media-WH",
)


EXPECTED_BUDGET_SHEETS = (
    "GGBE_2026_Jahresbudget",
    "WH_2026_Jahresbudget",
    "2025_Jahresbudget",
)
