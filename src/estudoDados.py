#%%
import requests
import pandas as pd
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env



headers = {
    "X-Auth-Token": os.getenv("FOOTBALL_API_TOKEN"),
    "Accept": "application/json"
}

#%%
def buscarDadosTimes(offset):
    try:
        url = f"http://api.football-data.org/v4/teams/?limit=10000&offset={offset}"
        print(f"Requesting data from URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        dados = response.json()

        while dados["count"] > 0:
            offset += 450

            url = f"http://api.football-data.org/v4/teams/?limit=10000&offset={offset}"
            print(f"Requesting data from URL: {url}")

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            new_data = response.json()
            dados["teams"].extend(new_data["teams"])

            if offset >= 450:
                break


        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"../dados/teams_{data_hora}.json", "w") as f:
            json.dump(dados["teams"], f, indent=4)        

    except Exception as e:
        print("Problema na requisição HTTP!")

        sleep_time = 60  # Tempo de espera em segundos
        print(f"Aguardando {sleep_time} segundos antes de tentar novamente...")
        time.sleep(sleep_time)

        buscarDadosTimes(offset)
    



#%% 
offset = 0
buscarDadosTimes(offset)

#%%
import pandas as pd

df = pd.read_json("../dados/teams_20260703_191119.json")  # Substitua pelo caminho correto do arquivo JSON

df.drop_duplicates()




#%%

from utils.api_client import FootballAPIClient

client = FootballAPIClient()

response = client.get_paginated(
    endpoint="v4/matches", data_key="matches")

response

#%%
from datetime import datetime, timezone

type(now)