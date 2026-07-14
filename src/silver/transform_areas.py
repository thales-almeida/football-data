from utils.config import BRONZE_PATH, SILVER_PATH
from utils.common import normalize_bronze_data, read_latest_bronze, upsert_silver_parquet
from datetime import datetime, timezone


def transform_areas():
    data, source_file = read_latest_bronze(
        bronze_base_path=BRONZE_PATH,
        endpoint_name="areas"
    )

    df = normalize_bronze_data(data)

    df = df.rename(columns={
        "id": "area_id",
        "name": "area_name",
        "flag": "area_flag",
        "country_code": "area_country_code",
        "parent_area": "continent"
    })

    for col in ["area_id", "parent_area_id"]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    for col in ["area_name", "area_flag", "area_country_code", "continent"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    df = df.dropna(subset=["area_id"])
    df = df.drop_duplicates(subset=["area_id"], keep="last")

    df["bronze_source_file"] = str(source_file)

    extracted_at = str(source_file).split("areas_")[1].split(".json")[0]
    dt_extracted_at = datetime.strptime(extracted_at, "%Y%m%dT%H%M%SZ")
    dt_extracted_at = dt_extracted_at.replace(tzinfo=timezone.utc)

    output_file = upsert_silver_parquet(
        df_new=df,
        silver_base_path=SILVER_PATH,
        table_name="areas",
        key_columns=["area_id"],
        extracted_at=dt_extracted_at.isoformat()
    )

    print(f"Silver areas atualizada: {output_file}")
    print(f"Registros processados nesta carga: {len(df)}")


if __name__ == "__main__":
    transform_areas()
