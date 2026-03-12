import pandas as pd


def preparar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor Renato"] = pd.to_numeric(df["Valor Renato"], errors="coerce").fillna(0)
    df["Valor Brunna"] = pd.to_numeric(df["Valor Brunna"], errors="coerce").fillna(0)
    df["Categoria"] = df["Categoria"].astype(str).str.strip().str.title()
    df["Total"] = df["Valor Renato"] + df["Valor Brunna"]
    return df


def preparar_orcamento(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Categoria"] = df["Categoria"].astype(str).str.strip().str.title()
    df["Orcamento"] = pd.to_numeric(df["Orcamento"], errors="coerce").fillna(0)
    df["Mes"] = pd.to_numeric(df["Mes"], errors="coerce").fillna(0).astype(int)
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").fillna(0).astype(int)
    return df


def preparar_historico(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"]).copy()
    df["Mes_Ref"] = df["Data"].dt.to_period("M").dt.to_timestamp()
    df["Mes_Str"] = df["Data"].dt.to_period("M").astype(str)
    df["Ano"] = df["Data"].dt.year
    df["Mes_Num"] = df["Data"].dt.month
    return df.sort_values("Mes_Ref")


def gerar_resumo_mensal(historico: pd.DataFrame) -> pd.DataFrame:
    resumo = (
        historico
        .groupby("Mes_Ref")["Total"]
        .sum()
        .reset_index()
        .sort_values("Mes_Ref")
    )

    resumo["Media_Movel_3M"] = resumo["Total"].rolling(window=3, min_periods=1).mean()
    resumo["Variacao_Mensal"] = resumo["Total"].diff()
    resumo["Variacao_Mensal_%"] = resumo["Total"].pct_change() * 100
    resumo["Variacao_Anual_%"] = resumo["Total"].pct_change(periods=12) * 100
    resumo["Ano"] = resumo["Mes_Ref"].dt.year
    resumo["Mes_Num"] = resumo["Mes_Ref"].dt.month
    resumo["Mes_Str"] = resumo["Mes_Ref"].dt.to_period("M").astype(str)
    return resumo


def filtrar_mes(historico: pd.DataFrame, ano: int, mes: int) -> pd.DataFrame:
    return historico[(historico["Ano"] == ano) & (historico["Mes_Num"] == mes)].copy()


def resumo_categorias(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Categoria", "Total"])

    return (
        df.groupby("Categoria")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=False)
    )


def calcular_resumo_divisao(df_mes: pd.DataFrame) -> dict:
    total_renato = df_mes["Valor Renato"].sum()
    total_brunna = df_mes["Valor Brunna"].sum()
    diferenca = total_renato - total_brunna

    if diferenca > 0:
        mensagem = "Brunna deve"
        valor_ajuste = abs(diferenca) / 2
        destino = "Renato"
    elif diferenca < 0:
        mensagem = "Renato deve"
        valor_ajuste = abs(diferenca) / 2
        destino = "Brunna"
    else:
        mensagem = "Está tudo equilibrado ✨"
        valor_ajuste = 0
        destino = ""

    return {
        "total_renato": total_renato,
        "total_brunna": total_brunna,
        "diferenca": diferenca,
        "mensagem_base": mensagem,
        "valor_ajuste": valor_ajuste,
        "destino": destino,
    }
