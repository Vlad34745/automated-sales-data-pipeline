"""
Пошук і об'єднання вхідних CSV-файлів.
"""
import glob
import logging
from pathlib import Path

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


class NoInputFilesError(FileNotFoundError):
    """Немає жодного вхідного файлу за очікуваним шаблоном."""


class MissingColumnsError(ValueError):
    """Вхідний файл не містить обов'язкових колонок."""


def find_input_files(data_dir: Path = config.RAW_DATA_DIR,
                      pattern: str = config.RAW_DATA_PATTERN) -> list[str]:
    """Знаходить усі файли, що відповідають шаблону, у відсортованому порядку."""
    file_paths = sorted(glob.glob(str(data_dir / pattern)))
    if not file_paths:
        raise NoInputFilesError(
            f"Не знайдено жодного файлу за шаблоном '{pattern}' у '{data_dir}'. "
            "Перевір, що CSV-файли лежать у папці raw_data."
        )
    logger.info("Знайдено %d файл(ів): %s", len(file_paths), file_paths)
    return file_paths


def load_and_merge(file_paths: list[str]) -> pd.DataFrame:
    """Читає та об'єднує список CSV-файлів в один DataFrame, з перевіркою колонок."""
    frames = []
    for path in file_paths:
        df = pd.read_csv(path)
        missing = set(config.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise MissingColumnsError(
                f"Файл '{path}' не містить обов'язкових колонок: {sorted(missing)}"
            )
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    logger.info("Об'єднано %d рядків з %d файл(ів).", len(merged), len(file_paths))
    return merged


def load_all_sales_data(data_dir: Path = config.RAW_DATA_DIR,
                         pattern: str = config.RAW_DATA_PATTERN) -> pd.DataFrame:
    """Зручна обгортка: знайти файли + завантажити + об'єднати."""
    file_paths = find_input_files(data_dir, pattern)
    return load_and_merge(file_paths)
