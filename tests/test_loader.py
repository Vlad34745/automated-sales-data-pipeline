from pathlib import Path

import pandas as pd
import pytest

from src.loader import (
    MissingColumnsError,
    NoInputFilesError,
    find_input_files,
    load_and_merge,
)


@pytest.fixture
def valid_csv(tmp_path: Path) -> Path:
    path = tmp_path / "large_sales_month1.csv"
    pd.DataFrame({
        "sale_id": [1, 2],
        "date": ["2026-01-01", "2026-01-02"],
        "product_name": ["A", "B"],
        "price": ["10", "20"],
        "quantity": [1, 2],
    }).to_csv(path, index=False)
    return path


def test_find_input_files_raises_when_no_files_match(tmp_path: Path):
    with pytest.raises(NoInputFilesError):
        find_input_files(data_dir=tmp_path, pattern="large_sales_month*.csv")


def test_find_input_files_finds_matching_files(valid_csv: Path, tmp_path: Path):
    found = find_input_files(data_dir=tmp_path, pattern="large_sales_month*.csv")
    assert len(found) == 1
    assert found[0].endswith("large_sales_month1.csv")


def test_load_and_merge_combines_multiple_files(tmp_path: Path):
    for i in (1, 2):
        pd.DataFrame({
            "sale_id": [i],
            "date": ["2026-01-01"],
            "product_name": ["A"],
            "price": ["10"],
            "quantity": [1],
        }).to_csv(tmp_path / f"large_sales_month{i}.csv", index=False)

    files = find_input_files(data_dir=tmp_path, pattern="large_sales_month*.csv")
    merged = load_and_merge(files)
    assert len(merged) == 2


def test_load_and_merge_raises_on_missing_required_column(tmp_path: Path):
    bad_path = tmp_path / "large_sales_month1.csv"
    pd.DataFrame({"sale_id": [1], "date": ["2026-01-01"]}).to_csv(bad_path, index=False)

    with pytest.raises(MissingColumnsError):
        load_and_merge([str(bad_path)])
