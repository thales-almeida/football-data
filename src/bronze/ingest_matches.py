from utils.api_client import FootballAPIClient
from utils.storage import save_json
from utils.config import BRONZE_PATH


def main():
    client = FootballAPIClient()

    matches = client.get(
        endpoint="v4/matches"
    )

    output_file = save_json(
        data=matches['matches'],
        endpoint_name="matches",
        base_path=BRONZE_PATH
    )

    print(f"{len(matches['matches'])} partidas extraídas.")
    print(f"Arquivo salvo em: {output_file}")


if __name__ == "__main__":
    main()