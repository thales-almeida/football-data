from utils.api_client import FootballAPIClient
from utils.storage import save_json
from utils.config import BRONZE_PATH


def main():
    client = FootballAPIClient()

    teams = client.get_paginated(
        endpoint="v4/teams",
        limit=500,
        data_key="teams"
    )

    output_file = save_json(
        data=teams,
        endpoint_name="teams",
        base_path=BRONZE_PATH
    )

    print(f"{len(teams)} times extraídos.")
    print(f"Arquivo salvo em: {output_file}")


if __name__ == "__main__":
    main()