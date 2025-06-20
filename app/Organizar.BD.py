import pandas as pd
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(BASE_DIR, "dados_loggi", "csv")
PASTA_SAIDA = PASTA  # Pode ajustar se quiser saída em outra pasta

def tratar_data(valor):
    if pd.isnull(valor):
        return pd.NaT
    valor = str(valor).strip()
    try:
        return pd.to_datetime(valor, dayfirst=True, errors='coerce')
    except Exception:
        return pd.NaT

def aguardar_arquivo_pronto(caminho, tentativas=10, intervalo=1):
    tamanho_anterior = -1
    for _ in range(tentativas):
        if not os.path.exists(caminho):
            time.sleep(intervalo)
            continue
        tamanho_atual = os.path.getsize(caminho)
        if tamanho_atual == tamanho_anterior and tamanho_atual > 1024:
            return True
        tamanho_anterior = tamanho_atual
        time.sleep(intervalo)
    return False

def organizar_dados():
    bases, ruas, arquivos_para_apagar = [], [], []
    for arquivo in os.listdir(PASTA):
        if arquivo.endswith(".csv"):
            caminho_csv = os.path.join(PASTA, arquivo)
            if not aguardar_arquivo_pronto(caminho_csv):
                print(f"Arquivo {arquivo} não está pronto para leitura. Pulando.")
                continue
            sigla = arquivo.replace(".csv", "")
            try:
                df = pd.read_csv(caminho_csv, sep=None, engine='python')
                while df.shape[1] < 7:
                    df[f'col_{df.shape[1]+1}'] = ""
                for nome_col_data in ["Prazo", "Data", "Data de entrega"]:
                    if nome_col_data in df.columns:
                        df[nome_col_data] = df[nome_col_data].apply(tratar_data)
                if df.shape[1] > 4:
                    df.iloc[:, 4] = df.iloc[:, 4].apply(tratar_data)
                df["base"] = sigla
                cols = list(df.columns)
                if cols[-1] != "base":
                    cols = [c for c in cols if c != "base"] + ["base"]
                    df = df[cols]
                df.to_csv(caminho_csv, sep=",", index=False, encoding="utf-8")
                if arquivo.endswith(".Base.csv"):
                    bases.append(df)
                    arquivos_para_apagar.append(caminho_csv)
                elif arquivo.endswith(".Rua.csv"):
                    ruas.append(df)
                    arquivos_para_apagar.append(caminho_csv)
            except Exception as e:
                print(f"Erro ao converter {arquivo}: {e}")

    time.sleep(5)
    if bases:
        arquivo_bases = os.path.join(PASTA, "BDB.geral.loggi.xlsx")
        df_bases_concat = pd.concat(bases, ignore_index=True)
        if 'Prazo' in df_bases_concat.columns:
            df_bases_concat['Prazo'] = pd.to_datetime(df_bases_concat['Prazo'], dayfirst=True, errors='coerce').dt.normalize()
        df_bases_concat.to_excel(arquivo_bases, index=False)
        print(f"Arquivo criado: {arquivo_bases}")

    if ruas:
        arquivo_ruas = os.path.join(PASTA, "BDR.geral.loggi.xlsx")
        df_ruas_concat = pd.concat(ruas, ignore_index=True)
        if 'Prazo' in df_ruas_concat.columns:
            df_ruas_concat['Prazo'] = pd.to_datetime(df_ruas_concat['Prazo'], dayfirst=True, errors='coerce').dt.normalize()
        df_ruas_concat.to_excel(arquivo_ruas, index=False)
        print(f"Arquivo criado: {arquivo_ruas}")

    for caminho in arquivos_para_apagar:
        try:
            os.remove(caminho)
            print(f"Arquivo removido: {caminho}")
        except Exception as e:
            print(f"Erro ao remover {caminho}: {e}")

    arquivo_base = os.path.join(PASTA, "BDB.geral.loggi.xlsx")
    arquivo_rua = os.path.join(PASTA, "BDR.geral.loggi.xlsx")
    arquivo_saida = os.path.join(PASTA_SAIDA, "Base_Rua_Juntos.xlsx")

    df_base = pd.read_excel(arquivo_base)
    df_rua = pd.read_excel(arquivo_rua)

    colunas_renomear = {
        "Status do pacote": "Status",
        "id do pacote": "ID do pacote",
        "Id do pacote": "ID do pacote"
    }
    df_base.rename(columns=colunas_renomear, inplace=True)
    df_rua.rename(columns=colunas_renomear, inplace=True)

    status_map = {
        "Sem tentativa": "Em base",
        "Aguardando reenvio": "Em base",
        "Aguardando tratativa":"Tratativa",
        "Arquivo integrado":"nulo",
        "Conferido":"nulo",
        "No centro de re-estoque":"nulo",
        "Pacote não encontrado":"nulo",
        "Pacote não retirado":"nulo",
        "Retornado para o cliente":"nulo",
        "Destinatário ausente": "Ausente",
        "Recusado pelo destinatário": "Recusado"
    }
    if "Status" in df_base.columns:
        df_base["Status"] = df_base["Status"].replace(status_map)
    if "Status" in df_rua.columns:
        df_rua["Status"] = df_rua["Status"].replace(status_map)

    colunas_desejadas = ["Prazo", "base", "Status", "ID do pacote"]
    df_base = df_base[[col for col in colunas_desejadas if col in df_base.columns]]
    df_rua = df_rua[[col for col in colunas_desejadas if col in df_rua.columns]]

    for df in [df_base, df_rua]:
        if 'Prazo' in df.columns:
            df['Prazo'] = pd.to_datetime(df['Prazo'], dayfirst=True, errors='coerce').dt.normalize()
    df_junto = pd.concat([df_base, df_rua], ignore_index=True)
    if 'base' in df_junto.columns:
        df_junto['base'] = df_junto['base'].str.replace(r'\.Rua$|\.Base$', '', regex=True)
    if 'Prazo' in df_junto.columns:
        df_junto['Prazo'] = pd.to_datetime(df_junto['Prazo'], dayfirst=True, errors='coerce').dt.normalize()
    df_junto.to_excel(arquivo_saida, index=False)
    print(f"Arquivo criado: {arquivo_saida}")

    print("Processamento concluído.")

if __name__ == "__main__":
    organizar_dados()