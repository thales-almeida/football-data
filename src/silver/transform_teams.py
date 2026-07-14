import pandas as pd

from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import normalize_bronze_data, read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_teams():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="teams"
    )

    df = normalize_bronze_data(data)

    df = df.rename(columns={
        "id": "team_id",
        "name": "team_name",
        "short_name": "team_short_name",
        "club_colors": "team_colors"
    })

    for col in ["team_id", "founded"]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    for col in ["team_name", "team_short_name", "tla", "crest", "venue", "website", "address", "team_colors"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(
            df["last_updated"], utc=True, errors="coerce"
        )

    df = df.dropna(subset=["team_id"])
    df = df.drop_duplicates(subset=["team_id"], keep="last")

    df["bronze_source_file"] = str(source_file)

    extracted_at = str(source_file).split("teams_")[1].split(".json")[0]
    dt_extracted_at = datetime.strptime(extracted_at, "%Y%m%dT%H%M%SZ")
    dt_extracted_at = dt_extracted_at.replace(tzinfo=timezone.utc)

    output_file = upsert_silver_parquet(
        df_new=df,
        silver_base_path=SILVER_PATH,
        table_name="teams",
        key_columns=["team_id"],
        extracted_at=dt_extracted_at.isoformat()
    )

    print(f"Silver teams atualizada: {output_file}")
    print(f"Registros processados nesta carga: {len(df)}")


if __name__ == "__main__":
    transform_teams()
