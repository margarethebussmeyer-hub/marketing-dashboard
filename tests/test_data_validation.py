from __future__ import annotations

import pandas as pd
import pytest

from src.data_validation import DataValidationError, validate_required_columns


def test_validate_required_columns_accepts_minimum_columns() -> None:
    frame = pd.DataFrame(
        {
            "calendar_week": [23],
            "new_followers": [24],
            "interactions": [179],
            "views": [65149],
        }
    )

    validate_required_columns(frame, "Gemüsegärtner")


def test_validate_required_columns_reports_missing_columns() -> None:
    frame = pd.DataFrame({"calendar_week": [23], "new_followers": [24]})

    with pytest.raises(DataValidationError, match="Pflichtspalten"):
        validate_required_columns(frame, "Gemüsegärtner")
