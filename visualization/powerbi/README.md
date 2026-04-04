# Power BI – Connecting to Finance Pipeline MySQL Mart Tables

This guide explains how to connect **Power BI Desktop** to the MySQL mart tables
produced by the dbt transformation layer.

---

## Prerequisites

- Power BI Desktop installed (latest version recommended)
- MySQL ODBC Driver 8.x or the MySQL connector for Power BI installed
- Access to the MySQL host (locally via Docker or a remote server)
- Credentials: host, port, database name, username, password

---

## Steps

1. **Open Power BI Desktop** and click **Get Data → More → MySQL Database**.

2. **Enter connection details**:
   - Server: `<MYSQL_HOST>` (e.g. `localhost` or your server IP)
   - Database: `finance_db`
   - Port: `3306` (append to server as `localhost:3306`)

3. **Enter credentials** when prompted (Database authentication):
   - Username: `<MYSQL_USER>`
   - Password: `<MYSQL_PASSWORD>`

4. **Select mart tables** to import:
   - `mart_monthly_summary`
   - `mart_category_breakdown`
   - `mart_top_merchants`

5. Click **Load** (or **Transform Data** to apply Power Query transformations first).

6. **Build your report** using the loaded tables as data sources.

---

## Recommended Visualisations

<!-- TODO: Add specific Power BI visual recommendations once mart schemas are finalised -->

- Monthly spend trend → Line or Clustered Bar chart from `mart_monthly_summary`
- Category breakdown → Donut or Pie chart from `mart_category_breakdown`
- Top merchants → Table or Bar chart from `mart_top_merchants`

---

## Scheduled Refresh

<!-- TODO: Document Power BI Gateway setup for scheduled refresh if using a remote MySQL server -->

For cloud-hosted MySQL, configure the **On-premises data gateway** in Power BI Service
to enable scheduled dataset refresh.
