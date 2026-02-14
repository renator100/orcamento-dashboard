import pandas as pd


def extrair_mes_ano(df):
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    if df["Data"].isna().all():
        raise ValueError("Coluna Data inválida ou vazia.")

    mes_ano = df["Data"].dt.to_period("M").mode()[0]

    return mes_ano.year, mes_ano.month
