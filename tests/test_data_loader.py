from __future__ import annotations

from pathlib import Path

from src.config import BRAND_GG, BRAND_WH, DashboardConfig
from src.data_loader import load_dashboard_data, normalize_brand


def test_normalize_brand_aliases() -> None:
    assert normalize_brand("GGBE") == BRAND_GG
    assert normalize_brand("GG") == BRAND_GG
    assert normalize_brand("WH") == BRAND_WH


def test_load_dashboard_data_from_new_workbooks() -> None:
    config = DashboardConfig()

    data = load_dashboard_data(Path(config.marketing_path), Path(config.budget_path))

    assert not data.acquisition.empty
    assert not data.social.empty
    assert not data.budget_categories.empty
    assert {BRAND_GG, BRAND_WH}.issubset(set(data.social["brand"]))
    assert data.budget_categories[data.budget_categories["is_total"]]["used"].sum() > 0
