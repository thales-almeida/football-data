from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON_BIN = PROJECT_ROOT / "venv" / "bin" / "python"
SOURCE_DIR = PROJECT_ROOT / "src"

SENSOR_CONFIG = {
    "allowed_states": ["success"],
    "failed_states": ["failed", "upstream_failed"],
    "skipped_states": ["skipped"],
    "check_existence": True,
    "mode": "reschedule",
    "poll_interval": 60,
    "timeout": 6 * 60 * 60,
}


with DAG(
    dag_id="football_matches_daily",
    description="Ingestao e upsert diario das partidas do Football Data",
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
    tags=["football-data", "matches"],
) as dag:
    wait_for_areas = ExternalTaskSensor(
        task_id="wait_for_areas",
        external_dag_id="football_areas_daily",
        external_task_id="transform_areas",
        **SENSOR_CONFIG,
    )

    wait_for_competitions = ExternalTaskSensor(
        task_id="wait_for_competitions",
        external_dag_id="football_competitions_daily",
        external_task_id="transform_competitions",
        **SENSOR_CONFIG,
    )

    wait_for_teams = ExternalTaskSensor(
        task_id="wait_for_teams",
        external_dag_id="football_teams_daily",
        external_task_id="transform_teams",
        **SENSOR_CONFIG,
    )

    ingest_matches = BashOperator(
        task_id="ingest_matches",
        bash_command=f"{PYTHON_BIN} -m bronze.ingest_matches",
        cwd=str(SOURCE_DIR),
    )

    transform_matches = BashOperator(
        task_id="transform_matches",
        bash_command=f"{PYTHON_BIN} -m silver.transform_matches",
        cwd=str(SOURCE_DIR),
    )

    [wait_for_areas, wait_for_competitions, wait_for_teams] >> ingest_matches
    ingest_matches >> transform_matches
