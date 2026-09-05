"""
Агрегація очищених даних у бізнес-звіти.
"""
import pandas as pd


def build_monthly_report(df: pd.DataFrame) -> pd.DataFrame:
    """Помісячна виручка, обсяг продажів і середній чек."""
    report = (
        df.groupby("year_month")
        .agg(
            total_sales_volume=("quantity_cleaned", "sum"),
            total_revenue_usd=("total_revenue", "sum"),
            average_ticket=("total_revenue", "mean"),
        )
        .sort_values("year_month")
        .reset_index()
    )
    report["year_month"] = report["year_month"].astype(str)
    return report


def build_product_report(df: pd.DataFrame) -> pd.DataFrame:
    """Продажі та виручка по кожному товару, відсортовані за виручкою."""
    return (
        df.groupby("product_name_cleaned")
        .agg(
            units_sold=("quantity_cleaned", "sum"),
            revenue_generated_usd=("total_revenue", "sum"),
        )
        .sort_values("revenue_generated_usd", ascending=False)
        .reset_index()
    )


def build_master_export(df: pd.DataFrame) -> pd.DataFrame:
    """Готує фінальний, охайно перейменований датасет для аркуша 'Cleaned Master Data'."""
    export = df[
        ["sale_id", "date_cleaned", "product_name_cleaned", "price_cleaned",
         "quantity_cleaned", "total_revenue"]
    ].copy()
    export.columns = ["Sale ID", "Date", "Product Name", "Unit Price", "Quantity", "Total Revenue"]
    export["Date"] = export["Date"].dt.strftime("%Y-%m-%d")
    return export
