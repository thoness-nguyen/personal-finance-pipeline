# 🏦 Personal Finance Data Pipeline

A full end-to-end personal finance data engineering project — from raw Excel/CSV input to automated ETL, cloud data lake, SQL data warehouse, dbt transformations, and interactive dashboards.

Built as a learning project covering **Data Engineering → DevOps → Data Science**.

---

## 🗺️ Architecture

```
[Excel / CSV Export]
        ↓
[Phase 1 – Ingestion]
  Python FastAPI (primary)  →  GCS Data Lake /raw
  Node.js Express (fallback) →  GCS Data Lake /raw  (flags needs_cleaning=true)
        ↓
[Phase 1B – Cleaning & Load]
  Python pandas cleans data  →  MySQL schema tables
  Cleaned file               →  GCS Data Lake /processed
        ↓
[Phase 2 – Transformation]
  dbt reads MySQL → staging models → mart models
        ↓
[Phase 3 – Visualization]
  Streamlit  (primary / data science)
  Power BI   (secondary)
  Looker Studio (tertiary)
        ↓
[Phase 4 – DevOps]
  GitHub Actions (ETL schedule, dbt tests, deploy)
  Docker (all services containerized)
        ↓
[Phase 5 – Data Science]
  Forecasting · Anomaly Detection · Clustering
```

---

## 🛠️ Tech Stack

| Layer                | Tool                                 |
| -------------------- | ------------------------------------ |
| Ingestion (primary)  | Python FastAPI                       |
| Ingestion (fallback) | Node.js Express                      |
| Data Lake            | Google Cloud Storage (GCS)           |
| Database             | MySQL 8.0                            |
| Transformation       | dbt                                  |
| Visualization        | Streamlit → Power BI → Looker Studio |
| Orchestration        | GitHub Actions                       |
| Containerization     | Docker + Docker Compose              |
| Data Science         | pandas, scikit-learn, Prophet        |

---

## 📁 Project Structure

```
personal-finance-pipeline/
├── ingestion/
│   ├── python_api/          # FastAPI primary ingestion service
│   └── nodejs_fallback/     # Express fallback ingestion service
├── orchestrator/            # Pipeline orchestration script
├── database/
│   ├── schema/              # MySQL DDL (init.sql)
│   └── migrations/          # Future schema migrations
├── transformation/
│   └── dbt_project/         # dbt staging + mart models
├── visualization/
│   ├── streamlit_app/       # Streamlit dashboard
│   ├── powerbi/             # Power BI setup guide
│   └── looker/              # Looker Studio setup guide
├── data_science/
│   └── notebooks/           # EDA, forecasting, anomaly detection
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── credentials/             # GCP key (git-ignored)
├── .env.example             # Environment variable template
├── docker-compose.yml       # All services orchestration
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Google Cloud account + GCS bucket
- MySQL (via Docker or Cloud SQL)

### Setup

1. Clone the repo
2. Copy `.env.example` → `.env` and fill in your values
3. Place your GCP service account key at `credentials/<project>-<service>-<purpose>-<env>.json`
4. Run Docker Compose to start all services:
   - Run full:`docker-compose up --build`
   - Run individual service: `docker-compose up -d --build <service_name>`
5. Access services:
   - FastAPI: `http://localhost:8000/docs`
   - Node.js Express: `http://localhost:3000/api/ingest`
   - Streamlit: `http://localhost:8501`

---

## 📋 Project Phases

| Phase    | Description                            | Status   |
| -------- | -------------------------------------- | -------- |
| Phase 1  | Ingestion (FastAPI + Node.js fallback) | 🔲 To Do |
| Phase 1B | Data Cleaning & MySQL Load             | 🔲 To Do |
| Phase 2  | dbt Transformations                    | 🔲 To Do |
| Phase 3  | Streamlit Visualization                | 🔲 To Do |
| Phase 4  | DevOps – Docker + GitHub Actions       | 🔲 To Do |
| Phase 5  | Data Science – Forecasting & ML        | 🔲 To Do |

---

## 🔒 Security Notes

- Never commit `.env` or `credentials/` to Git (both are in `.gitignore`)
- Use GitHub Secrets for CI/CD environment variables

---

## 🔄 Local Database Sync

GitHub Actions runs the ETL pipeline daily and uploads the cleaned data to GCS, but it uses an **ephemeral MySQL container** that is destroyed after the job ends. To keep your local MySQL up to date, use `sync_local.ps1`.

### How it works

```
22:00 ICT  GitHub Actions ETL runs → uploads processed CSV to GCS
22:30 ICT  sync_local.ps1 fires    → pulls GCS → inserts only NEW rows into local MySQL
```

Only genuinely new rows are inserted — re-running the sync when nothing changed results in `inserted=0`.

### Setup (run once as Administrator)

```powershell
cd personal-finance-pipeline
powershell -ExecutionPolicy Bypass -File .\sync_local.ps1 -Register
```

### Run sync manually (anytime)

```powershell
# Via Task Scheduler
Start-ScheduledTask -TaskName "FinancePipeline-LocalSync"

# Or directly
powershell -ExecutionPolicy Bypass -File .\sync_local.ps1
```

### Check sync logs

```powershell
Get-Content .\logs\sync_local.log -Tail 30
```

### Check scheduled task status

```powershell
Get-ScheduledTaskInfo -TaskName "FinancePipeline-LocalSync"
```

### Disable (pause without removing)

```powershell
Disable-ScheduledTask -TaskName "FinancePipeline-LocalSync"

# Re-enable later
Enable-ScheduledTask -TaskName "FinancePipeline-LocalSync"
```

### Remove permanently

```powershell
powershell -ExecutionPolicy Bypass -File .\sync_local.ps1 -Unregister
```
