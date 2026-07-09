import json
from pathlib import Path
from datetime import datetime, timezone


def save_json(
    data: dict,
    endpoint_name: str,
    base_path: str
) -> str:
    extracted_at = datetime.now(timezone.utc)
    timestamp_file = extracted_at.strftime("%Y%m%dT%H%M%SZ")

    output_dir = Path(base_path) / endpoint_name 
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{endpoint_name}_{timestamp_file}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return str(output_file)