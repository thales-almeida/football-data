import pandas as pd

from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_competitions():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="competitions"
    )

    df = pd.json_normalize(data)

    df = df.rename(columns={
        "id": "competition_id",
        "name": "competition_name",
        "type": "competition_type",
        "code": "competition_code",
        "numberOfAvailableSeasons": "number_of_available_seasons",
    })

    expected_columns = [
        "competition_id",
        "competition_name",
        "competition_code",
        "competition_type",
        "area_id",
        "emblem",
        "plan",
        "current_season_id",
        "number_of_available_seasons"
    ]

    df = df[[col for col in expected_columns if col in df.columns]]

    for col in ["competition_id", "area_id", "current_season_id", "number_of_available_seasons"]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    for col in ["competition_name", "competition_code", "competition_type", "emblem", "plan"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    df = df.dropna(subset=["competition_id"])
    df = df.drop_duplicates(subset=["competition_id"], keep="last")

    df["bronze_source_file"] = str(source_file)

    extracted_at = str(source_file).split("competitions_")[1].split(".json")[0]
    dt_extracted_at = datetime.strptime(extracted_at, "%Y%m%dT%H%M%SZ")
    dt_extracted_at = dt_extracted_at.replace(tzinfo=timezone.utc)

    output_file = upsert_silver_parquet(
        df_new=df,
        silver_base_path=SILVER_PATH,
        table_name="competitions",
        key_columns=["competition_id"],
        extracted_at=dt_extracted_at.isoformat()
    )

    print(f"Silver competitions atualizada: {output_file}")
    print(f"Registros processados nesta carga: {len(df)}")


if __name__ == "__main__":
    transform_competitions()