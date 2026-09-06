"""
Функції очищення сирих даних.
Кожна функція чиста (не має побічних ефектів) і приймає/повертає
pandas Series або DataFrame — це робить їх легко тестованими окремо.
"""
import logging

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def clean_product_names(names: pd.Series) -> pd.Series:
    """
    Прибирає зайві пробіли, підставляє значення за замовчуванням для
    пропусків і зводить регістр до Title Case, з винятками для назв,
    які Title Case ламає (iPhone, iPad, Wi-Fi).

    На відміну від жорстко захардкодженого словника відповідностей,
    цей підхід автоматично об'єднує будь-які регістрові варіації
    (напр. 'MACBOOK air', 'macbook Air') без потреби заздалегідь
    перелічувати кожен можливий варіант.
    """
    # Пропуски визначаються ДО .astype(str), а не після — pandas.isna()
    # надійно працює на будь-якій версії pandas. Якщо перевіряти "nan" як
    # рядок вже після приведення до str, результат залежить від версії:
    # у pandas 2.x None перетворюється на рядок 'None', а в pandas 3.x
    # лишається як NaN. Такий баг реально ловився в CI (pandas 2.3.3),
    # хоча локально під pandas 3.0.2 все виглядало робочим.
    is_missing = names.isna()
    cleaned = names.astype(str).str.strip()
    cleaned = cleaned.mask(is_missing, config.DEFAULT_PRODUCT_NAME)
    # Додатковий запобіжник на випадок, якщо "nan"/"None" все ж просочиться
    # рядком (напр. якщо джерело вже містило такий текст як значення).
    cleaned = cleaned.replace({"nan": config.DEFAULT_PRODUCT_NAME, "None": config.DEFAULT_PRODUCT_NAME})

    def normalize(name: str) -> str:
        exception = config.PRODUCT_NAME_EXCEPTIONS.get(name.lower())
        if exception:
            return exception
        return name.title()

    return cleaned.map(normalize)


def clean_prices(prices: pd.Series, product_names: pd.Series) -> pd.Series:
    """
    Прибирає символи валюти/пробіли/коми з ціни та конвертує в float.
    Пропущені значення заповнюються медіаною ціни для того самого товару
    (а не глобальним середнім), щоб не спотворювати дешеві/дорогі категорії.
    """
    # Символьний клас [\$,\s] прибирає $, кому, пробіл;
    # окремий патерн USD прибирає слово цілком (а не літери U/S/D нарізно).
    cleaned = prices.astype(str).str.replace(r"[\$,\s]|USD", "", regex=True)
    cleaned = pd.to_numeric(cleaned, errors="coerce")

    n_missing_before = cleaned.isna().sum()
    cleaned = cleaned.groupby(product_names).transform(lambda s: s.fillna(s.median()))

    n_missing_after = cleaned.isna().sum()
    if n_missing_after:
        logger.warning(
            "%d цін залишились незаповненими (немає жодної відомої ціни для товару).",
            n_missing_after,
        )
    else:
        logger.info("Заповнено %d пропущених цін медіаною по товару.", n_missing_before)

    return cleaned


def clean_quantities(quantities: pd.Series) -> pd.Series:
    """Заповнює пропущені кількості значенням за замовчуванням і приводить до int."""
    return quantities.fillna(config.DEFAULT_QUANTITY).astype(int)


def clean_dates(dates: pd.Series) -> pd.Series:
    """
    Парсить дати, змішані в кількох форматах, за пріоритетним списком
    форматів (config.DATE_FORMATS), а не покладаючись на автоматичне
    вгадування pandas (format='mixed'), яке для неоднозначних дат
    (напр. '10/02/2026') може помилково визначити місяць та день місцями.
    """
    stripped = dates.astype(str).str.split(" ").str[0]
    result = pd.Series(pd.NaT, index=dates.index, dtype="datetime64[ns]")

    for fmt in config.DATE_FORMATS:
        still_missing = result.isna()
        if not still_missing.any():
            break
        attempt = pd.to_datetime(stripped[still_missing], format=fmt, errors="coerce")
        result.loc[still_missing] = attempt

    n_unparsed = result.isna().sum()
    if n_unparsed:
        logger.warning("%d дат не вдалося розпізнати жодним з відомих форматів.", n_unparsed)
    else:
        logger.info("Усі дати успішно розпізнано (0 неопрацьованих).")

    return result


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Застосовує всі кроки очищення до сирого DataFrame і повертає новий DataFrame."""
    df = df.copy()

    df["product_name_cleaned"] = clean_product_names(df["product_name"])
    df["price_cleaned"] = clean_prices(df["price"], df["product_name_cleaned"])
    df["quantity_cleaned"] = clean_quantities(df["quantity"])
    df["date_cleaned"] = clean_dates(df["date"])
    df["year_month"] = df["date_cleaned"].dt.to_period("M")
    df["total_revenue"] = df["price_cleaned"] * df["quantity_cleaned"]

    return df