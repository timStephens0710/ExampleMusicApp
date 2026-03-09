from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from datetime import datetime
import logging
import requests
import time

# ──────────────────────────────────────────
# DAG CONFIGURATION
# ──────────────────────────────────────────

# Tables to extract from PostgreSQL and load into Snowflake RAW
# These map directly to your Django model table names
TABLES = [
    'music_app_auth_customuser',
    'music_app_archive_playlist',
    'music_app_archive_track',
    'music_app_archive_streaminglink',
]

# Airflow connection IDs - these must match what you configured in Admin → Connections
POSTGRES_CONN_ID = 'postgres_music_app'
SNOWFLAKE_CONN_ID = 'snowflake_music_app'

# ──────────────────────────────────────────
# TASK FUNCTIONS
# ──────────────────────────────────────────

def extract_from_postgres(**context):
    """
    Task 1: Extract data from PostgreSQL (Django app database)

    - Connects to the Django PostgreSQL DB using the postgres_music_app connection
    - Reads all rows from each table defined in TABLES
    - Pushes the data to Airflow's XCom so the next task can access it

    XCom (Cross Communication) is Airflow's built-in way of passing data between tasks.
    """
    logging.info("Starting extraction from PostgreSQL")

    # PostgresHook uses the connection we configured in the Airflow UI
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    extracted_data = {}

    for table in TABLES:
        logging.info(f"Extracting table: {table}")
        
        # Get a connection and execute a simple SELECT *
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        
        # Fetch column names and all rows
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        extracted_data[table] = {
            'columns': columns,
            'rows': rows
        }
        
        logging.info(f"Extracted {len(rows)} rows from {table}")
        cursor.close()
        conn.close()

    # Push extracted data to XCom so load_to_snowflake_raw can access it
    context['ti'].xcom_push(key='extracted_data', value=extracted_data)
    logging.info("Extraction complete — data pushed to XCom")


def load_to_snowflake_raw(**context):
    """
    Task 2: Load extracted data into Snowflake RAW schema

    - Pulls the extracted data from XCom (passed from Task 1)
    - Connects to Snowflake using the snowflake_music_app connection
    - Creates the table in RAW if it doesn't exist
    - Truncates and reloads the table on each run (full refresh)
    - This is a simple approach suitable for small datasets
    """
    logging.info("Starting load to Snowflake RAW")

    # Pull the data that Task 1 pushed to XCom
    extracted_data = context['ti'].xcom_pull(
        key='extracted_data',
        task_ids='extract_from_postgres'
    )

    if not extracted_data:
        raise ValueError("No data received from extract_from_postgres task")

    # SnowflakeHook uses the connection we configured in the Airflow UI
    snowflake_hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = snowflake_hook.get_conn()
    cursor = conn.cursor()

    # Set the context for all subsequent SQL commands
    cursor.execute("USE DATABASE MUSIC_APP_DB")
    cursor.execute("USE SCHEMA RAW")
    cursor.execute("USE WAREHOUSE MUSIC_APP_WH")
    cursor.execute("USE ROLE MUSIC_APP_ROLE")

    for table_name, data in extracted_data.items():
        columns = data['columns']
        rows = data['rows']

        logging.info(f"Loading {len(rows)} rows into RAW.{table_name}")

        # Build CREATE TABLE IF NOT EXISTS statement
        # All columns created as VARCHAR for simplicity - dbt handles type casting in staging
        column_definitions = ', '.join([f'"{col}" VARCHAR' for col in columns])
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {column_definitions}
            )
        """
        cursor.execute(create_sql)

        # Truncate the table before reloading to avoid duplicates on re-runs
        cursor.execute(f"TRUNCATE TABLE {table_name}")

        # Insert all rows
        if rows:
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.executemany(insert_sql, rows)

        logging.info(f"Successfully loaded {table_name} into Snowflake RAW")

    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Load to Snowflake RAW complete")


def _trigger_dbt_job(job_type: str) -> None:
    """
    Shared helper function used by both trigger_dbt_run and trigger_dbt_test.

    - Retrieves the API token securely from Airflow connections (dbt_cloud)
    - Retrieves account ID and job ID from Airflow variables
    - Triggers the dbt Cloud job via the API
    - Polls every 10 seconds until the job completes
    - Raises an exception if the job fails so Airflow marks the task as failed

    Args:
        job_type: Label used in log messages e.g. 'run' or 'test'
    """
    # Retrieve API token from Airflow connections — never hardcoded in code
    dbt_conn = BaseHook.get_connection('dbt_cloud')
    api_token = dbt_conn.password

    # Retrieve account and job IDs from Airflow variables
    account_id = Variable.get('DBT_ACCOUNT_ID')
    job_id = Variable.get('DBT_JOB_ID')

    # Log config for debugging — never log the api_token itself
    logging.info(f"dbt Cloud config — account_id: {account_id}, job_id: {job_id}")
    logging.info(f"API token retrieved: {'YES' if api_token else 'NO — check dbt_cloud connection'}")

    headers = {
        'Authorization': f'Token {api_token}',
        'Content-Type': 'application/json'
    }

    # Trigger the dbt Cloud job
    trigger_url = f'https://uh837.us1.dbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/'
    logging.info(f"Triggering dbt {job_type} — POST {trigger_url}")

    response = requests.post(
        trigger_url,
        headers=headers,
        json={'cause': f'Triggered by Airflow — dbt {job_type}'}
    )

    # Log the full API response for debugging
    logging.info(f"API response status code: {response.status_code}")
    logging.info(f"API response body: {response.text}")

    # Raise immediately if the API call itself failed (e.g. 401 unauthorised, 404 not found)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"dbt Cloud API call failed — status {response.status_code}. "
            f"Check your API token, account ID and job ID are correct. "
            f"Full error: {e}"
        )

    run_id = response.json()['data']['id']
    logging.info(f"dbt {job_type} triggered successfully — run ID: {run_id}")

    # Poll the API every 10 seconds until the job finishes
    status_url = f'https://uh837.us1.dbt.com/api/v2/accounts/{account_id}/runs/{run_id}/'
    logging.info(f"Polling run status at: {status_url}")

    poll_count = 0
    while True:
        time.sleep(10)
        poll_count += 1

        status_response = requests.get(status_url, headers=headers)

        # Log polling response for debugging
        logging.info(f"Poll #{poll_count} — status code: {status_response.status_code}")

        try:
            status_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to poll dbt run status — full error: {e}")

        run_data = status_response.json()['data']
        status = run_data['status']
        status_message = run_data.get('status_humanized', status)

        logging.info(f"Poll #{poll_count} — dbt {job_type} status: {status_message} (code: {status})")

        # dbt Cloud status codes:
        # 1 = Queued, 2 = Starting, 3 = Running, 10 = Success, 20 = Error, 30 = Cancelled
        if status == 10:
            logging.info(f"dbt {job_type} completed successfully after {poll_count} polls")
            break
        elif status in [20, 30]:
            # Log the full run data to help diagnose what failed
            logging.error(f"dbt {job_type} failed — full run data: {run_data}")
            raise Exception(
                f"dbt {job_type} failed with status: {status_message} (code: {status}). "
                f"Run ID: {run_id}. Check dbt Cloud Deploy → Runs for full error details."
            )


def trigger_dbt_run(**context):
    """
    Task 3: Trigger dbt run to transform RAW → STAGING → MARTS

    - Calls the shared _trigger_dbt_job helper
    - Triggers the dbt Cloud job and waits for completion
    - Fails the Airflow task if dbt run fails
    """
    logging.info("Starting dbt run — RAW → STAGING → MARTS")
    _trigger_dbt_job(job_type='run')
    logging.info("dbt run completed successfully")


def trigger_dbt_test(**context):
    """
    Task 4: Trigger dbt test to validate data quality

    - Calls the shared _trigger_dbt_job helper
    - Only runs if Task 3 (dbt run) succeeded
    - Fails the Airflow task if any dbt tests fail
    """
    logging.info("Starting dbt test — validating data quality across all models")
    _trigger_dbt_job(job_type='test')
    logging.info("dbt test completed successfully — all data quality checks passed")


# ──────────────────────────────────────────
# DAG DEFINITION
# ──────────────────────────────────────────

with DAG(
    dag_id='music_app_pipeline',                    # Unique identifier - shown in Airflow UI
    description='Extracts data from PostgreSQL, loads into Snowflake RAW, triggers dbt run',
    schedule_interval=None,                          # None = manual trigger only
    start_date=datetime(2026, 3, 9),                # Historical start date - required by Airflow
    catchup=False,                                   # Don't backfill historical runs
    tags=['music_app', 'etl', 'snowflake', 'dbt'],  # Tags for filtering in the UI
) as dag:

    # Task 1 — Extract from PostgreSQL
    extract = PythonOperator(
        task_id='extract_from_postgres',
        python_callable=extract_from_postgres,
    )

    # Task 2 — Load into Snowflake RAW
    load = PythonOperator(
        task_id='load_to_snowflake_raw',
        python_callable=load_to_snowflake_raw,
    )

    # Task 3 — Trigger dbt run
    dbt_run = PythonOperator(
        task_id='trigger_dbt_run',
        python_callable=trigger_dbt_run,
    )
    
    # Task 4 — Trigger dbt test
    dbt_test = PythonOperator(
        task_id='trigger_dbt_test',
        python_callable=trigger_dbt_test,
    )

    # ── Dependency Chain ──
    # This defines the order of execution:
    # extract → load → dbt
    # Each task only runs if the previous one succeeds
    extract >> load >> dbt_run >> dbt_test