import pandas as pd

from src.reporting import build_master_export, build_monthly_report, build_product_report


def make_clean_df() -> pd.DataFrame:
    return pd.DataFrame({
        "sale_id": [1, 2, 3],
        "date_cleaned": pd.to_datetime(["2026-01-01", "2026-01-15", "2026-02-01"]),
        "year_month": pd.to_datetime(["2026-01-01", "2026-01-15", "2026-02-01"]).to_period("M"),
        "product_name_cleaned": ["A", "B", "A"],
        "price_cleaned": [100.0, 50.0, 100.0],
        "quantity_cleaned": [1, 2, 3],
        "total_revenue": [100.0, 100.0, 300.0],
    })


def test_monthly_report_aggregates_by_month():
    report = build_monthly_report(make_clean_df())
    assert list(report["year_month"]) == ["2026-01", "2026-02"]
    jan = report[report["year_month"] == "2026-01"].iloc[0]
    assert jan["total_sales_volume"] == 3  # 1 + 2
    assert jan["total_revenue_usd"] == 200.0  # 100 + 100


def test_product_report_sorted_by_revenue_descending():
    report = build_product_report(make_clean_df())
    assert report.iloc[0]["product_name_cleaned"] == "A"  # 400 revenue > B's 100
    assert report.iloc[0]["revenue_generated_usd"] == 400.0
    assert report.iloc[0]["units_sold"] == 4  # 1 + 3


def test_master_export_has_renamed_columns_and_string_dates():
    export = build_master_export(make_clean_df())
    assert list(export.columns) == [
        "Sale ID", "Date", "Product Name", "Unit Price", "Quantity", "Total Revenue",
    ]
    assert export["Date"].iloc[0] == "2026-01-01"
