from pathlib import Path

import pandas as pd
import pytest

from src.pipeline import run


@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    pd.DataFrame({
        "sale_id": [1, 2, 3],
        "date": ["2026-01-01", "2026-01-15", "10/02/2026"],
        "product_name": [" macbook air ", "iPhone 15 Pro", None],
        "price": ["$100", "200 USD", None],
        "quantity": [1, 2, None],
    }).to_csv(tmp_path / "large_sales_month1.csv", index=False)
    return tmp_path


def test_run_produces_a_readable_excel_file(sample_data_dir: Path, tmp_path: Path):
    output_path = tmp_path / "output" / "report.xlsx"
    output_path.parent.mkdir()

    result_path = run(data_dir=sample_data_dir, output_path=output_path)

    assert result_path == output_path
    assert output_path.exists()


def test_run_end_to_end_produces_correct_business_numbers(sample_data_dir: Path, tmp_path: Path):
    output_path = tmp_path / "report.xlsx"

    run(data_dir=sample_data_dir, output_path=output_path)

    master = pd.read_excel(output_path, sheet_name="Cleaned Master Data")
    monthly = pd.read_excel(output_path, sheet_name="Monthly Performance")
    product = pd.read_excel(output_path, sheet_name="Product Performance")

    assert len(master) == 3
    # Пропущений product_name має стати 'Unknown Product', а не 'nan'/'None'
    assert "Unknown Product" in product["product_name_cleaned"].tolist()
    # Усі три рядки з тестових даних потрапляють у Q1 2026 (Січень/Лютий)
    assert set(monthly["year_month"]) == {"2026-01", "2026-02"}


def test_run_raises_clear_error_when_no_input_files(tmp_path: Path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        run(data_dir=empty_dir, output_path=tmp_path / "report.xlsx")
