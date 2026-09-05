"""
Оркестрація повного пайплайну: завантаження -> очищення -> звіти -> експорт.
"""
import logging
from pathlib import Path

from src import config, exporter, loader, reporting
from src.cleaning import clean_sales_data

logger = logging.getLogger(__name__)


def run(data_dir: Path = config.RAW_DATA_DIR, output_path: Path = config.OUTPUT_FILE) -> Path:
    """Запускає весь пайплайн і повертає шлях до згенерованого Excel-файлу."""
    raw_df = loader.load_all_sales_data(data_dir)
    clean_df = clean_sales_data(raw_df)

    monthly_report = reporting.build_monthly_report(clean_df)
    product_report = reporting.build_product_report(clean_df)
    master_export = reporting.build_master_export(clean_df)

    logger.info("=== MONTHLY BUSINESS PERFORMANCE REPORT ===\n%s",
                monthly_report.to_string(index=False))
    logger.info("=== TOP PRODUCTS BY REVENUE REPORT ===\n%s",
                product_report.to_string(index=False))

    return exporter.export_report(master_export, monthly_report, product_report, output_path)
