# Automated Sales Data Cleaning & Business Intelligence Pipeline

## 📌 Project Overview
This project demonstrates an end-to-end data analytics pipeline designed to process, clean, and standardize messy, multi-month retail sales data. The pipeline dynamically unifies incoming reports, handles complex text and data type inconsistencies, repairs faulty chronological records, and exports clean executive-ready reports into a multi-sheet stylized Excel workbook.

## 🛠️ Tech Stack & Tools
- **Language:** Python 3.14+
- **Libraries:** Pandas, Glob, OpenPyXL, Sys, Subprocess
- **Environment:** Isolated Virtual Environment (`venv`)
- **IDE:** VS Code / Jupyter Notebooks

## ⚡ Key Pipeline Architecture

### 1. Dynamic Dataset Discovery & Merging
Instead of hardcoding filenames, the pipeline utilizes the `glob` module to automatically discover all files matching the pattern `data/large_sales_month*.csv`. This ensures scalability, enabling the pipeline to process 3, 12, or 50 months of data without changing a single line of code.

### 2. Multi-Pass Advanced Date Parsing
The source files contained severe date formatting chaos (e.g., `YYYY/MM/DD HH:MM`, `DD/MM/YYYY`, and `MM-DD-YYYY` mixed together). Standard auto-parsing led to severe data drift. 
- Implemented a custom iterative parsing function (`clean_mixed_dates`) using structured priority fallback formats.
- Achieved **100% conversion accuracy** (0 unparsed dates remaining) and restored correct chronological alignment for 15,000 transactions strictly into Q1 2026.

### 3. Intelligent Data Imputation & Text Cleaning
- **Price Extraction:** Used Regular Expressions (Regex) to strip formatting clutter (`$`, `USD`, spaces, commas) and cast values to numeric `float64`.
- **Contextual Imputation:** Missing values ($NaN$) in prices were intelligently filled by calculating the **median price of that specific product group** rather than a blunt global average.
- **Text Standardization:** Fixed casing duplicates (e.g., `iphone 15 pro` vs `iPhone 15 Pro`) and trimmed trailing whitespaces to prevent reporting fragmentation.
- **Quantity Fixes:** Imputed missing values with a baseline of `1` unit and converted the feature to an explicit `int` type.

### 4. Corporate-Grade Excel Intelligence Export
Utilizing `openpyxl`, the pipeline generates a professional multi-sheet spreadsheet (`final_sales_analytics_report.xlsx`) featuring:
- **Cleaned Master Data:** All 15,000 polished transactions with **frozen header panes** for effortless scrolling.
- **Executive Summaries:** Automated monthly performance trends and top-grossing product reports.
- **Strict Visual Design:** Consistent typography (`Segoe UI`), deep corporate blue header blocks (`#1F4E78`), dynamic column auto-fitting (no cropped text or `###` errors), and accurate currency formatting (`$#,##0.00`).

## 🚀 How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Vlad34745/sales-data-pipeline.git](https://github.com/Vlad34745/sales-data-pipeline.git)
   cd sales-data-pipeline