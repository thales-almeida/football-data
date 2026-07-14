import pandas as pd

from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import normalize_bronze_data, read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_matches():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="matches"
    )

    df = normalize_bronze_data(data)

    df = df.rename(columns={
        "id": "match_id",
        "utc_date": "match_date",
        "status": "match_status",
        "stage": "match_stage",
    })

    integer_columns = [
        "area_id",
        "competition_id",
        "match_id",
        "matchday",
        "season_id",
        "season_current_matchday",
        "season_winner_id",
        "season_winner_founded",
        "home_team_id",
        "away_team_id",
        "score_half_time_home",
        "score_half_time_away",
        "score_full_time_home",
        "score_full_time_away"
    ]
    for col in integer_columns:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    datetime_columns = [
        "match_date",
        "last_updated",
        "season_start_date",
        "season_end_date",
        "season_winner_last_updated"
    ]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    df = df.dropna(subset=["match_id"])
    df = df.drop_duplicates(subset=["match_id"], keep="last")

    df["bronze_source_file"] = str(source_file)

    extracted_at = str(source_file).split("matches_")[1].split(".json")[0]
    dt_extracted_at = datetime.strptime(extracted_at, "%Y%m%dT%H%M%SZ")
    dt_extracted_at = dt_extracted_at.replace(tzinfo=timezone.utc)

    output_file = upsert_silver_parquet(
        df_new=df,
        silver_base_path=SILVER_PATH,
        table_name="matches",
        key_columns=["match_id"],
        extracted_at=dt_extracted_at.isoformat()
    )

    print(f"Silver matches atualizada: {output_file}")
    print(f"Registros processados nesta carga: {len(df)}")


if __name__ == "__main__":
    transform_matches()
