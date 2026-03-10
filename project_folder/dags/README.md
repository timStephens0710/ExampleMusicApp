# music_app_pipeline — Airflow DAG

This DAG orchestrates the full data pipeline for the Music Archiving App. It extracts data from the Django PostgreSQL database, loads it into Snowflake's RAW schema, then triggers dbt Cloud to transform and test the data.

---

## Pipeline Overview

```
PostgreSQL (Django DB)
        │
        ▼
[Task 1] extract_from_postgres
        │
        ▼
[Task 2] load_to_snowflake_raw
        │
        ▼
[Task 3] trigger_dbt_run       ← RAW → STAGING → MARTS
        │
        ▼
[Task 4] trigger_dbt_test      ← Data quality validation
```

Each task only runs if the previous one succeeds. The DAG is manually triggered (no schedule).

---

## Tasks

### Task 1 — `extract_from_postgres`

Connects to the Django app's PostgreSQL database and extracts all rows from the following tables:

| Table | Description |
|---|---|
| `music_app_auth_customuser` | Django custom user model |
| `music_app_archive_playlist` | User playlists |
| `music_app_archive_track` | Archived tracks |
| `music_app_archive_streaminglink` | Streaming service links per track |

Extracted data (column names + rows) is passed to the next task via Airflow XCom.

---

### Task 2 — `load_to_snowflake_raw`

Pulls the extracted data from XCom and loads it into Snowflake's `RAW` schema.

- Creates tables if they do not already exist — all columns stored as `VARCHAR`
- Truncates and fully reloads on every run (full refresh strategy)
- Type casting and business logic are handled downstream by dbt, not here

---

### Task 3 — `trigger_dbt_run`

Triggers a dbt Cloud job via the dbt Cloud API and polls every 10 seconds until it completes.

- Transforms `RAW` → `STAGING` → `MARTS`
- Fails the Airflow task if the dbt job errors or is cancelled, surfacing the failure in the UI

---

### Task 4 — `trigger_dbt_test`

Triggers the same dbt Cloud job in test mode and polls until completion.

- Runs dbt data quality tests across all models
- Only executes if Task 3 succeeded
- Fails the Airflow task if any dbt tests fail

---

## Airflow Connections Required

Configure these in the Airflow UI under **Admin → Connections** before running the DAG.

| Connection ID | Type | Purpose |
|---|---|---|
| `postgres_music_app` | Postgres | Django app PostgreSQL database |
| `snowflake_music_app` | Snowflake | Snowflake data warehouse |
| `dbt_cloud` | HTTP | dbt Cloud API — API token stored in the `password` field |

---

## Airflow Variables Required

Configure these in the Airflow UI under **Admin → Variables**.

| Variable Key | Description |
|---|---|
| `DBT_ACCOUNT_ID` | Your dbt Cloud account ID |
| `DBT_JOB_ID` | The ID of the dbt Cloud job to trigger |

> The dbt API token is retrieved from the `dbt_cloud` connection's `password` field, not from a variable. Never store secrets in Airflow Variables.

---

## Snowflake Setup

The DAG expects the following to exist in Snowflake before running:

```sql
-- Required objects
ROLE:      MUSIC_APP_ROLE
WAREHOUSE: MUSIC_APP_WH
DATABASE:  MUSIC_APP_DB
SCHEMA:    MUSIC_APP_DB.RAW
```

RAW tables are created automatically by the DAG on first run if they do not exist.

---

## DAG Configuration

| Setting | Value |
|---|---|
| `dag_id` | `music_app_pipeline` |
| `schedule_interval` | `None` — manual trigger only |
| `start_date` | `2026-03-09` |
| `catchup` | `False` |
| `tags` | `music_app`, `etl`, `snowflake`, `dbt` |

---

## Running the DAG

1. Ensure all Connections and Variables above are configured in the Airflow UI
2. Navigate to **DAGs** and search for `music_app_pipeline`
3. Toggle the DAG on if it is paused
4. Click **Trigger DAG** to run manually

---

## Error Handling

| Failure point | What happens |
|---|---|
| PostgreSQL connection fails | Task 1 errors; downstream tasks do not run |
| No data extracted | Task 2 raises `ValueError` and fails |
| Snowflake connection / SQL fails | Task 2 errors; dbt tasks do not run |
| dbt API call fails (4xx/5xx) | Task 3 or 4 raises HTTP exception with status code |
| dbt job errors or is cancelled | Task 3 or 4 raises exception with run ID for debugging |
| dbt tests fail | Task 4 errors; run ID logged for inspection in dbt Cloud |

Check **dbt Cloud → Deploy → Runs** for full step-level logs when a dbt task fails.
