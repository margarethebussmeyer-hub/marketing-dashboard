from __future__ import annotations

import pandas as pd

from src.data_processing import build_discount_code_overview


def test_discount_code_overview_groups_voucher_uses() -> None:
    frame = pd.DataFrame(
        {
            "brand": ["Gemüsegärtner", "Gemüsegärtner", "Weidenhof"],
            "report_year": [2026, 2026, 2026],
            "voucher_name": ["Pflanze 26", "Pflanze 26", "/"],
            "uses": [10, 5, 99],
            "channel": ["Offline", "Offline", "Online"],
            "start_date": pd.to_datetime(["2026-05-01", "2026-05-08", "2026-01-01"]),
        }
    )

    overview = build_discount_code_overview(frame)

    assert overview.loc[0, "discount_code"] == "Pflanze 26"
    assert overview.loc[0, "uses"] == 15
