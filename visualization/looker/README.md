# Looker Studio – Connecting to Finance Pipeline MySQL / BigQuery

This guide explains how to connect **Looker Studio** (formerly Google Data Studio)
to the MySQL mart tables or a BigQuery export from the finance pipeline.

---

## Option A: Connect Directly to MySQL

1. Open [Looker Studio](https://lookerstudio.google.com) and click **Create → Report**.
2. Click **Add data** and search for **MySQL**.
3. Enter connection details:
   - Host: `<MYSQL_HOST>`
   - Port: `3306`
   - Database: `finance_db`
   - Username: `<MYSQL_USER>`
   - Password: `<MYSQL_PASSWORD>`
4. Select the mart tables:
   - `mart_monthly_summary`
   - `mart_category_breakdown`
   - `mart_top_merchants`
5. Click **Connect** and then **Add to report**.

---

## Option B: Connect via BigQuery (Recommended for Production)

<!-- TODO: Document BigQuery export step once GCS → BigQuery pipeline is implemented -->

1. Export MySQL mart tables to BigQuery using a scheduled Cloud Dataflow job or
   a dbt-bigquery adapter profile.
2. In Looker Studio, click **Add data → BigQuery**.
3. Select your GCP project, dataset (`finance_db`), and tables.
4. Click **Add** and build your report.

---

## Recommended Charts

<!-- TODO: Update with specific field names once mart schemas are finalised -->

- **Monthly spend trend**: Time series chart from `mart_monthly_summary`
- **Category breakdown**: Pie chart from `mart_category_breakdown`
- **Top merchants**: Bar chart or table from `mart_top_merchants`

---

## Sharing & Scheduling

Looker Studio reports can be shared via link or embedded. Scheduled email delivery
is available under **Share → Schedule email delivery**.
