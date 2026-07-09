import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


def get_latest_bronze_file(
    bronze_base_path: str,
    endpoint_name: str
) -> Path:
    endpoint_path = Path(bronze_base_path) / endpoint_name

    print(endpoint_path)

    files = sorted(endpoint_path.glob("*.json"))

    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo JSON encontrado para o endpoint: {endpoint_name}"
        )

    return files[-1]


def read_latest_bronze(
    bronze_base_path: str,
    endpoint_name: str
) -> tuple[dict | list, Path]:
    latest_file = get_latest_bronze_file(
        bronze_base_path=bronze_base_path,
        endpoint_name=endpoint_name
    )

    with open(latest_file, "r", encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, dict):
        data = payload.get("data", payload)

    elif isinstance(payload, list):
        data = payload

    else:
        raise ValueError(
            f"Estrutura inesperada no arquivo Bronze: {latest_file}"
        )

    return data, latest_file


def upsert_silver_parquet(
    df_new: pd.DataFrame,
    silver_base_path: str,
    table_name: str,
    key_columns: list[str],
    extracted_at: str | None = None
) -> str:
    output_dir = Path(silver_base_path) / table_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{table_name}.parquet"

    now = datetime.now(timezone.utc).isoformat()

    df_new = df_new.copy()

    df_new["last_seen_at"] = extracted_at
    df_new["updated_at_silver"] = now

    if not output_file.exists():
        df_new["created_at_silver"] = now
        df_new.to_parquet(output_file, index=False)
        return str(output_file)

    df_current = pd.read_parquet(output_file)

    if "created_at_silver" not in df_current.columns:
        df_current["created_at_silver"] = now

    current_created_at = df_current[
        key_columns + ["created_at_silver"]
    ].drop_duplicates(subset=key_columns)

    df_new = df_new.merge(
        current_created_at,
        on=key_columns,
        how="left"
    )

    df_new["created_at_silver"] = df_new["created_at_silver"].fillna(now)

    keys_new = df_new[key_columns].drop_duplicates()
    keys_new["_exists_in_new_file"] = True

    df_current_not_updated = df_current.merge(
        keys_new,
        on=key_columns,
        how="left"
    )

    df_current_not_updated = df_current_not_updated[
        df_current_not_updated["_exists_in_new_file"].isna()
    ].drop(columns=["_exists_in_new_file"])

    df_final = pd.concat(
        [df_current_not_updated, df_new],
        ignore_index=True
    )

    df_final = df_final.drop_duplicates(
        subset=key_columns,
        keep="last"
    )

    df_final.to_parquet(output_file, index=False)

    return str(output_file)
