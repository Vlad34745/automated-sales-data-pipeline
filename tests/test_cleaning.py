import pandas as pd
import pytest

from src.cleaning import (
    clean_dates,
    clean_prices,
    clean_product_names,
    clean_quantities,
    clean_sales_data,
)


class TestCleanProductNames:
    def test_strips_whitespace(self):
        result = clean_product_names(pd.Series([" Powerbank 65W "]))
        assert result.iloc[0] == "Powerbank 65W"

    def test_fills_missing_with_default(self):
        result = clean_product_names(pd.Series([None, "iPhone 15 Pro"]))
        assert result.iloc[0] == "Unknown Product"

    def test_merges_case_variants_without_hardcoded_list(self):
        # 'macbook air', 'MACBOOK AIR', 'MacBook Air' мають звестись до одного значення,
        # навіть якщо цього конкретного написання немає в PRODUCT_NAME_EXCEPTIONS.
        result = clean_product_names(pd.Series(["macbook air", "MACBOOK AIR", "MacBook Air"]))
        assert result.nunique() == 1

    def test_known_exceptions_keep_correct_casing(self):
        result = clean_product_names(pd.Series(["iphone 15 pro", "ipad air", "wi-fi adapter"]))
        assert list(result) == ["iPhone 15 Pro", "iPad Air", "Wi-Fi Adapter"]

    def test_internal_capitals_not_flattened_by_title_case(self):
        # Regression: .title() саме по собі перетворює "MacBook" -> "Macbook"
        # і "AirPods" -> "Airpods" — ці випадки мають бути у винятках.
        result = clean_product_names(pd.Series(["macbook air", "macbook pro", "airpods pro"]))
        assert list(result) == ["MacBook Air", "MacBook Pro", "AirPods Pro"]


class TestCleanPrices:
    def test_strips_currency_symbols(self):
        products = pd.Series(["A", "A"])
        prices = pd.Series(["$599.00", "599 USD"])
        result = clean_prices(prices, products)
        assert result.iloc[0] == 599.00
        assert result.iloc[1] == 599.00

    def test_fills_missing_with_group_median(self):
        products = pd.Series(["A", "A", "A"])
        prices = pd.Series(["100", None, "300"])
        result = clean_prices(prices, products)
        assert result.iloc[1] == 200.0  # медіана групи 'A': (100, 300) -> 200

    def test_does_not_leak_median_across_products(self):
        products = pd.Series(["A", "A", "B", "B"])
        prices = pd.Series(["100", "200", "1000", None])
        result = clean_prices(prices, products)
        assert result.iloc[3] == 1000.0  # має взяти медіану групи 'B', а не 'A'


class TestCleanQuantities:
    def test_fills_missing_with_default_and_casts_to_int(self):
        result = clean_quantities(pd.Series([1.0, None, 3.0]))
        assert result.tolist() == [1, 1, 3]
        assert result.dtype == int


class TestCleanDates:
    def test_parses_iso_format(self):
        result = clean_dates(pd.Series(["2026-01-15"]))
        assert result.iloc[0] == pd.Timestamp("2026-01-15")

    def test_parses_slash_format(self):
        result = clean_dates(pd.Series(["2026/01/15"]))
        assert result.iloc[0] == pd.Timestamp("2026-01-15")

    def test_parses_day_month_year_as_day_first_not_month_first(self):
        # Це regression-тест на баг, знайдений у оригінальному ноутбуці:
        # pd.to_datetime(..., format='mixed') вгадував '10/02/2026' як
        # 2 жовтня замість 10 лютого. clean_dates має явний пріоритет
        # форматів і завжди трактує такий рядок як DD/MM/YYYY.
        result = clean_dates(pd.Series(["10/02/2026"]))
        assert result.iloc[0] == pd.Timestamp("2026-02-10")

    def test_strips_time_component(self):
        result = clean_dates(pd.Series(["2026/02/27 04:00"]))
        assert result.iloc[0] == pd.Timestamp("2026-02-27")

    def test_unparseable_date_becomes_nat(self):
        result = clean_dates(pd.Series(["not-a-date"]))
        assert pd.isna(result.iloc[0])


class TestCleanSalesData:
    def test_full_pipeline_produces_expected_columns(self):
        df = pd.DataFrame({
            "sale_id": [1, 2],
            "date": ["2026-01-01", "10/02/2026"],
            "product_name": ["macbook air", "iphone 15 pro"],
            "price": ["$100", "200 USD"],
            "quantity": [2.0, None],
        })
        result = clean_sales_data(df)

        expected_cols = {
            "product_name_cleaned", "price_cleaned", "quantity_cleaned",
            "date_cleaned", "year_month", "total_revenue",
        }
        assert expected_cols.issubset(result.columns)
        assert result["total_revenue"].iloc[0] == 200.0  # 100 * 2
        assert result["date_cleaned"].iloc[1] == pd.Timestamp("2026-02-10")

    def test_no_row_ordering_or_count_lost(self):
        df = pd.DataFrame({
            "sale_id": [1, 2, 3],
            "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "product_name": ["A", "B", "C"],
            "price": ["10", "20", "30"],
            "quantity": [1, 1, 1],
        })
        result = clean_sales_data(df)
        assert len(result) == 3
        assert list(result["sale_id"]) == [1, 2, 3]
