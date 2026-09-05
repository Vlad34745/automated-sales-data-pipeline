"""
Точка входу: python main.py

Читає всі raw_data/large_sales_month*.csv, очищує дані та зберігає
фінальний звіт у final_sales_analytics_report.xlsx.
"""
import logging

from src.pipeline import run

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    output_path = run()
    print(f"[SUCCESS] Звіт збережено у: {output_path}")
