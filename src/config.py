"""
Централізовані налаштування пайплайну.
Змінюй значення тут, а не в коді логіки — так легше підлаштувати
пайплайн під інші дані без ризику зламати обробку.
"""
from pathlib import Path

# --- Шляхи ---
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "raw_data"
RAW_DATA_PATTERN = "large_sales_month*.csv"
OUTPUT_FILE = BASE_DIR / "final_sales_analytics_report.xlsx"

# --- Очікувані колонки у вхідних CSV ---
REQUIRED_COLUMNS = ["sale_id", "date", "product_name", "price", "quantity"]

# --- Формати дат, які трапляються у вихідних файлах (у порядку пріоритету) ---
DATE_FORMATS = [
    "%Y-%m-%d",  # 2026-01-15
    "%Y/%m/%d",  # 2026/01/15
    "%d/%m/%Y",  # 15/01/2026
    "%m-%d-%Y",  # 01-15-2026
]

# --- Значення за замовчуванням для відсутніх даних ---
DEFAULT_PRODUCT_NAME = "Unknown Product"
DEFAULT_QUANTITY = 1

# --- Продукти, назви яких .title() ламає (внутрішні великі літери: iPhone, MacBook, AirPods) ---
PRODUCT_NAME_EXCEPTIONS = {
    "iphone 15 pro": "iPhone 15 Pro",
    "ipad air": "iPad Air",
    "macbook air": "MacBook Air",
    "macbook pro": "MacBook Pro",
    "airpods pro": "AirPods Pro",
    "wi-fi adapter": "Wi-Fi Adapter",
}

# --- Excel-стилі ---
HEADER_FONT_NAME = "Segoe UI"
HEADER_FONT_COLOR = "FFFFFF"
HEADER_FILL_COLOR = "1F4E78"
CURRENCY_FORMAT = "$#,##0.00"
INTEGER_FORMAT = "#,##0"
