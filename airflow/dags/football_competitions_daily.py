from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON_BIN = PROJECT_ROOT / "venv" / "bin" / "python"
SOURCE_DIR = PROJECT_ROOT / "src"


with DAG(
    dag_id="football_competitions_daily",
    description="Ingestao e upsert diario das competicoes do Football Data",
    schedule="@daily",
    start_date=datetime(2026, 7, 14, tzinfo=timezone.utc),
    catchup=False,
    is_paused_upon_creation=False,
    max_active_runs=1,
    default_args={
        "owner": "football_data",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["football-data", "competitions"],
) as dag:
    ingest_competitions = BashOperator(
        task_id="ingest_competitions",
        bash_command=f"{PYTHON_BIN} -m bronze.ingest_competitions",
        cwd=str(SOURCE_DIR),
    )

    transform_competitions = BashOperator(
        task_id="transform_competitions",
        bash_command=f"{PYTHON_BIN} -m silver.transform_competitions",
        cwd=str(SOURCE_DIR),
    )

    ingest_competitions >> transform_competitions
