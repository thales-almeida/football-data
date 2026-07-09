import time
import requests
from utils.config import API_BASE_URL, API_TOKEN


class FootballAPIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {
            "X-Auth-Token": API_TOKEN
        }

        # Limite da API: 10 chamadas por minuto
        self.min_interval_seconds = 6
        self.last_request_time = 0

    def _wait_rate_limit(self):
        """
        Garante que exista um intervalo mínimo entre chamadas.
        Como o limite é 10/minuto, aguardamos pelo menos 6 segundos.
        """
        elapsed_time = time.time() - self.last_request_time

        if elapsed_time < self.min_interval_seconds:
            wait_time = self.min_interval_seconds - elapsed_time
            time.sleep(wait_time)

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
        max_retries: int = 3
    ) -> dict:
        url = f"{self.base_url}{endpoint}"

        for attempt in range(1, max_retries + 1):
            self._wait_rate_limit()

            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            print(f"Requesting data from URL: {response.url} (Attempt {attempt}/{max_retries})")

            self.last_request_time = time.time()

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    wait_time = int(retry_after)
                else:
                    wait_time = 60

                print(
                    f"Limite da API atingido. "
                    f"Aguardando {wait_time} segundos. "
                    f"Tentativa {attempt}/{max_retries}."
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()

            return response.json()

        raise Exception(
            f"Erro 429 persistente após {max_retries} tentativas para o endpoint {endpoint}"
        )

    def get_paginated(
        self,
        endpoint: str,
        params: dict | None = None,
        limit: int = 500,
        data_key: str | None = None,
        max: int = 0
    ) -> list:
        all_records = []
        offset = 0

        try:
            while True:
                page_params = params.copy() if params else {}
                page_params["limit"] = limit
                page_params["offset"] = offset

                response_json = self.get(endpoint, params=page_params)

                if data_key:
                    records = response_json.get(data_key, [])
                else:
                    records = response_json

                if not records:
                    break

                all_records.extend(records)

                if len(records) == 0:
                    break

                offset += limit
                
                if max > 0 and len(all_records) >= max:
                    all_records = all_records[:max]
                    break
                
        except Exception as e:
            print(f"Problema com a requisição! Erro: {e}")

        return all_records 