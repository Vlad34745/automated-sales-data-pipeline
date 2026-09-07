# Automated Sales Data Cleaning & Business Intelligence Pipeline

![CI](https://github.com/Vlad34745/automated-sales-data-pipeline/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Vlad34745/automated-sales-data-pipeline/branch/main/graph/badge.svg)](https://codecov.io/gh/Vlad34745/automated-sales-data-pipeline)

## 📌 Project Overview

This project is an end-to-end data analytics pipeline that processes, cleans, and standardizes messy,
multi-month retail sales data. It dynamically unifies incoming monthly reports, repairs inconsistent
text and date formats, and exports clean, executive-ready reports into a multi-sheet, styled Excel
workbook.

The core logic lives in a tested, importable Python package (`src/`), reused identically by:
- `main.py` — a CLI entry point for production runs,
- `data_cleaning.ipynb` — a step-by-step exploratory walkthrough for portfolio/demo purposes.

Keeping one source of truth for the cleaning logic avoids the classic notebook trap of exploratory
code drifting out of sync with what actually ends up in the exported report.

## 🛠️ Tech Stack & Tools

- **Language:** Python 3.10 – 3.12
- **Libraries:** Pandas, OpenPyXL
- **Testing:** Pytest, pytest-cov
- **CI:** GitHub Actions (tests run on every push/PR across 3 Python versions)

## ⚡ Key Pipeline Architecture

### 1. Dynamic Dataset Discovery & Merging (`src/loader.py`)

Uses `glob` to automatically discover all files matching `raw_data/large_sales_month*.csv`, so the
pipeline scales to any number of monthly reports without code changes. Each file is validated against
a list of required columns before merging, and a missing/empty input directory raises a clear,
actionable error instead of a confusing pandas stack trace.

### 2. Priority-Ordered Date Parsing (`src/cleaning.py::clean_dates`)

Source files mix four date formats (`YYYY-MM-DD`, `YYYY/MM/DD`, `DD/MM/YYYY`, `MM-DD-YYYY`).
Naive auto-parsing (`pd.to_datetime(..., format='mixed')`) misreads ambiguous dates like `10/02/2026`
as `MM/DD/YYYY` (October) instead of `DD/MM/YYYY` (February) — silently corrupting the monthly
breakdown. `clean_dates` instead tries each format in an explicit priority order, only touching values
still unparsed by the previous format, giving **100% conversion accuracy** with no ambiguity.

### 3. Robust Text & Price Cleaning (`src/cleaning.py`)

- **Product names:** whitespace-trimmed and title-cased, with an explicit exception list for names
  Title Case breaks (`iPhone`, `MacBook`, `AirPods`, `Wi-Fi`). This merges arbitrary case variants
  (`macbook air`, `MACBOOK AIR`, `MacBook Air`) automatically, instead of relying on a hardcoded
  lookup table that silently misses any new variant.
- **Prices:** currency symbols, commas, and the literal word `USD` are stripped via regex, then cast
  to `float64`. Missing prices are filled with the **median price of that specific product**, not a
  blunt global average.
- **Quantities:** missing values default to `1` and are cast to `int`.

### 4. Corporate-Grade Excel Export (`src/exporter.py`)

Generates a multi-sheet `final_sales_analytics_report.xlsx` via `openpyxl`, featuring frozen header
panes, consistent typography (`Segoe UI`), deep corporate-blue header blocks (`#1F4E78`), dynamic
column auto-fitting, and currency formatting (`$#,##0.00`).

## ✅ Testing & CI

The cleaning, loading, and reporting logic is covered by a `pytest` suite (`tests/`), including a
regression test for the ambiguous-date bug described above. Every push and pull request to `main`
runs the full test suite plus an end-to-end smoke run of the pipeline, on Python 3.10, 3.11, and 3.12,
via GitHub Actions (`.github/workflows/ci.yml`). Coverage is tracked and reported by
[Codecov](https://codecov.io/gh/Vlad34745/automated-sales-data-pipeline).

Run the tests locally:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 🚀 How to Run the Project

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Vlad34745/automated-sales-data-pipeline.git
   cd automated-sales-data-pipeline
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the pipeline:**

   ```bash
   python main.py
   ```

   Or open `data_cleaning.ipynb` in VS Code / Jupyter for the step-by-step walkthrough. Sample data
   is already included in `raw_data/`, so both entry points work out of the box.

5. **Output:** A styled `final_sales_analytics_report.xlsx` is generated in the project root,
   containing the cleaned master dataset plus monthly and product performance summaries.

## 📂 Project Structure

```
automated-sales-data-pipeline/
├── .github/workflows/ci.yml   # CI: tests + smoke run on every push/PR
├── src/
│   ├── config.py               # All tunable settings in one place
│   ├── loader.py                # File discovery, merging, column validation
│   ├── cleaning.py              # Product name / price / quantity / date cleaning
│   ├── reporting.py             # Monthly & product aggregations
│   ├── exporter.py              # Styled multi-sheet Excel export
│   └── pipeline.py              # Orchestrates the full run
├── tests/                      # Pytest suite (incl. date-parsing regression test)
├── main.py                     # CLI entry point
├── data_cleaning.ipynb         # Exploratory, narrated walkthrough (uses src/)
├── raw_data/                   # Sample input CSVs
├── requirements.txt
└── requirements-dev.txt
```