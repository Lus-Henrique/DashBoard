import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tokens_dir = os.path.join(BASE_DIR, "..", "tokens")
token_file = os.path.join(tokens_dir, "token_id.txt")

def get_token():
    if not os.path.exists(token_file):
        raise Exception(f"Token não encontrado em {token_file}")
    with open(token_file, "r") as f:
        return f.read().strip()

def atualizar_dados_loggi():
    token = get_token()
    pasta = os.path.join(BASE_DIR, "dados_loggi", "csv")
    os.makedirs(pasta, exist_ok=True)

    # Bases para puxar os dados (ajuste as URLs e IDs conforme necessário)
    bases = [
        # ...mesma lista de dicionários que você já usa...
    ]

    # Baixa arquivos .Rua.csv
    for base in bases:
        params = {
            "timezone": "-0300",
            "view": "rua",
            "token": token,
            "distribution_center_id": base["distribution_center_id"],
            "last_mile_company_id": base["last_mile_company_id"],
            "routing_code": base["routing_code"],
            "companyType": "LEVE"
        }
        arquivo = os.path.join(pasta, f"{base['sigla']}.Rua.csv")
        response = requests.get(base["url"], params=params)
        if response.status_code == 200:
            with open(arquivo, "wb") as f:
                f.write(response.content)
            print(f"Arquivo salvo em: {arquivo}")
        else:
            print(f"Erro ao baixar {base['sigla']}: {response.status_code}")

    # Baixa arquivos .Base.csv (v1)
    params_base = {
        "timezone": "-0300",
        "view": "base"
    }
    for base in bases:
        params = params_base.copy()
        params["distribution_center_id"] = base["distribution_center_id"]
        params["last_mile_company_id"] = base["last_mile_company_id"]
        params["routing_code"] = base["routing_code"]
        headers = {"Authorization": f"Bearer {token}"}
        filename = os.path.join(pasta, f"{base['sigla']}.Base.csv")
        response = requests.get(base["url"], params=params, headers=headers)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Salvo como {filename}")
        else:
            print(f"Erro ao baixar {base['sigla']}: {response.status_code}")

if __name__ == "__main__":
    atualizar_dados_loggi()