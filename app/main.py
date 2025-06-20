from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_RUA = os.path.join(BASE_DIR, "dados_loggi", "csv", "Base_Rua_Juntos.xlsx")
EXCEL_BASE = os.path.join(BASE_DIR, "dados_loggi", "csv", "BDR.geral.loggi.xlsx")

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

STATUS_PERMITIDOS = ["Em base", "Retirado", "Ausente", "Endereço errado", "Recusado"]

@app.get("/", response_class=HTMLResponse)
def index(request: Request, prazo: str = Query(None), base2: str = Query(None)):
    df1 = pd.read_excel(EXCEL_RUA)
    df1.columns = df1.columns.str.strip()
    df1["Prazo_str"] = pd.to_datetime(df1["Prazo"], errors="coerce").dt.strftime("%Y-%m-%d")
    df1 = df1[df1["Status"].isin(STATUS_PERMITIDOS)]
    bases = sorted(df1["base"].dropna().unique())
    prazos_disponiveis = sorted(df1["Prazo_str"].dropna().unique())

    if prazo:
        df1 = df1[df1["Prazo_str"] == prazo]

    tabela = {
        base: {status: df1[(df1["base"] == base) & (df1["Status"] == status)]["ID do pacote"].count()
               for status in STATUS_PERMITIDOS}
        for base in bases
    }

    total_geral = {status: sum(tabela[base][status] for base in bases) for status in STATUS_PERMITIDOS}
    total_geral_geral = sum(total_geral.values())

    df2 = pd.read_excel(EXCEL_BASE)
    df2.columns = df2.columns.str.strip()
    df2["Prazo_str"] = pd.to_datetime(df2["Prazo"], errors="coerce").dt.strftime("%Y-%m-%d")
    if prazo:
        df2 = df2[df2["Prazo_str"] == prazo]
    if base2:
        df2 = df2[df2["base"] == base2]

    entregadores = sorted(df2["Entregador"].dropna().unique())
    status_titulos = ["Retirado", "Ocorrencia"]
    tabela2 = {
        ent: {
            "Retirado": df2[(df2["Entregador"] == ent) & (df2["Status do pacote"] == "Retirado")]["Id do pacote"].count(),
            "Ocorrencia": df2[(df2["Entregador"] == ent) & (df2["Status do pacote"] != "Retirado")]["Id do pacote"].count()
        } for ent in entregadores
    }

    total_geral2 = {k: sum(tabela2[e][k] for e in entregadores) for k in status_titulos}
    total_geral_geral2 = sum(total_geral2.values())

    ultima_atualizacao = datetime.datetime.fromtimestamp(os.path.getmtime(EXCEL_RUA)).strftime('%d/%m/%Y %H:%M:%S')

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabela": tabela,
        "bases": bases,
        "status_permitidos": STATUS_PERMITIDOS,
        "prazos": prazos_disponiveis,
        "prazo_selecionado": prazo,
        "total_geral": total_geral,
        "total_geral_geral": total_geral_geral,
        "tabela2": tabela2,
        "entregadores": entregadores,
        "status_titulos": status_titulos,
        "bases2": bases,
        "base2_selecionada": base2,
        "total_geral2": total_geral2,
        "total_geral_geral2": total_geral_geral2,
        "ultima_atualizacao": ultima_atualizacao
    })