from utils.api_client import FootballAPIClient
from utils.storage import save_json
from utils.config import BRONZE_PATH


def main():
    client = FootballAPIClient()

    areas = client.get(
        endpoint="v4/areas" 
    )

    output_file = save_json(
        data=areas['areas'],
        endpoint_name="areas",
        base_path=BRONZE_PATH
    )

    print(f"{len(areas['areas'])} areas extraídas.")
    print(f"Arquivo salvo em: {output_file}")


if __name__ == "__main__":
    main()