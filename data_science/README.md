# Data Science – Phase 5 Overview

This directory contains all Phase 5 data science work for the Personal Finance Pipeline:
exploratory data analysis (EDA), time-series forecasting, and anomaly detection.

---

## What Will Be Built Here

### 1. Exploratory Data Analysis (`notebooks/01_eda.ipynb`)
- Load expense data from MySQL mart tables using SQLAlchemy.
- Profile distributions of spend by category, merchant, and time period.
- Identify seasonal patterns, outliers, and data quality issues.
- Generate visualisations to guide feature engineering for forecasting.

### 2. Monthly Spend Forecasting (`notebooks/02_forecasting.ipynb`)
- Train a **Prophet** model on monthly aggregated spend from `mart_monthly_summary`.
- Optionally compare with **ARIMA** (via `statsmodels`) for benchmark.
- Generate 3-month forward forecasts with uncertainty intervals.
- Export forecast outputs to a `predictions` table in MySQL for the Streamlit dashboard.

### 3. Anomaly Detection (`notebooks/03_anomaly_detection.ipynb`)
- Apply **Isolation Forest** or **Z-score** method (via `scikit-learn`) to flag
  unusual transactions in the `expenses` table.
- Visualise anomalies on a scatter/timeline plot.
- Export flagged transaction IDs back to MySQL for the Streamlit dashboard.

---

## Trained Model Artefacts

Serialised model files (`.pkl`, `.json`) will be saved in `models/` and version-controlled
using `.gitkeep`. Large model files should be stored in GCS instead.

<!-- TODO: Add model versioning strategy (MLflow or manual versioning) -->

---

## Dependencies

See `requirements.txt` in this directory. Install with:

```bash
pip install -r data_science/requirements.txt
```

---

## Running Notebooks

```bash
cd data_science
jupyter notebook
```
