from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
import logging

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


def trigger_dbt_run(**context):
    """
    Task 3: Trigger dbt to transform RAW → STAGING → MARTS

    - This task uses the dbt Cloud API to trigger a job run
    - dbt handles all transformations from RAW through to your mart models
    - In a local dbt Core setup this would run the dbt CLI directly

    Note: For now this task logs a placeholder message.
    Once your dbt Cloud job is configured, replace this with the API call.
    """
    logging.info("Triggering dbt run")
    logging.info("dbt transformation: RAW → STAGING → MARTS")

    # ── Placeholder for dbt Cloud API trigger ──
    # When ready, configure a dbt Cloud job and add your account ID,
    # job ID and API key to trigger it via the dbt Cloud API here.
    # 
    # Example:
    # import requests
    # response = requests.post(
    #     f"https://cloud.getdbt.com/api/v2/accounts/{ACCOUNT_ID}/jobs/{JOB_ID}/run/",
    #     headers={"Authorization": f"Token {DBT_API_KEY}"},
    #     json={"cause": "Triggered by Airflow"}
    # )
    
    logging.info("dbt run triggered successfully")


def trigger_dbt_test(**context):
    """
    Task 4: Trigger dbt to run the tests

    - This task uses the dbt Cloud API to trigger a job run
    - dbt handles all transformations from RAW through to your mart models
    - In a local dbt Core setup this would run the dbt CLI directly

    Note: For now this task logs a placeholder message.
    Once your dbt Cloud job is configured, replace this with the API call.
    """
    logging.info("Triggering dbt test")    
    logging.info("dbt test triggered successfully")


# ──────────────────────────────────────────
# DAG DEFINITION
# ──────────────────────────────────────────

with DAG(
    dag_id='music_app_pipeline',                    # Unique identifier - shown in Airflow UI
    description='Extracts data from PostgreSQL, loads into Snowflake RAW, triggers dbt run',
    schedule_interval=None,                          # None = manual trigger only
    start_date=datetime(2026, 1, 1),                # Historical start date - required by Airflow
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