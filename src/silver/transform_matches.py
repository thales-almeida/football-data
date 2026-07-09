import pandas as pd

from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_matches():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="matches"
    )

    df = pd.json_normalize(data)

    df = df.rename(columns={
        "id": "match_id",
        "utcDate": "match_date",
        "status": "match_status",
        "stage": "match_stage",
        "homeTeam_id": "home_team_id",
        "awayTeam_id": "away_team_id"
    })

    expected_columns = [
        "area_id",
        "competition_id",
        "match_id",
        "match_date",
        "match_stage",
        "home_team_id",
        "away_team_id",
        "score_winner",
        "score_duration",
        "score_halfTime_home",
        "score_halfTime_away",
        "score_fullTime_home",
        "score_fullTime_away"
    ]

    df = df[[col for col in expected_columns if col in df.columns]]

    for col in ["area_id", "competition_id", "match_id", "home_team_id", "away_team_id", "score_halfTime_home", "score_halfTime_away", "score_fullTime_home", "score_fullTime_away"]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    for col in ["score_winner", "score_duration"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

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