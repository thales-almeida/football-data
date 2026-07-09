import pandas as pd

from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_teams():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="teams"
    )

    df = pd.json_normalize(data)

    df = df.rename(columns={
        "id": "team_id",
        "name": "team_name",
        "shortName": "team_short_name",
        "clubColors": "team_colors"
    })

    expected_columns = [
        "team_id",
        "team_name",
        "team_short_name",
        "tla",
        "founded",
        "team_colors",
        "venue",
        "website",
        "address",
        "crest"
    ]

    df = df[[col for col in expected_columns if col in df.columns]]

    for col in ["team_id", "founded"]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    for col in ["team_name", "team_short_name", "tla", "crest", "venue", "website", "address", "team_colors"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

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