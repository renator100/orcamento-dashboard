import os
import pandas as pd
from modules.utils import salvar_parquet_seguro

CAMINHO_DESPESAS = "dados/historico_despesas.parquet"
CAMINHO_ORCAMENTOS = "dados/historico_orcamentos.parquet"



def carregar_historico(caminho):
    if os.path.exists(caminho):
        return pd.read_parquet(caminho)
    return pd.DataFrame()



def salvar_historico(df, caminho):
    salvar_parquet_seguro(df, caminho)



def remover_mes(df, ano, mes):
    if df.empty:
        return df

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    filtro = ~((df["Data"].dt.year == ano) & (df["Data"].dt.month == mes))
    return df[filtro]
