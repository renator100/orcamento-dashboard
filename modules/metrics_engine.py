import pandas as pd


def gerar_resumo_mensal(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Ano", "Mes", "Total"])

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])

    resumo_mensal = (
        df.groupby([df["Data"].dt.year.rename("Ano"), df["Data"].dt.month.rename("Mes")])["Total"]
        .sum()
        .reset_index()
        .sort_values(["Ano", "Mes"])
        .reset_index(drop=True)
    )

    return resumo_mensal


def calcular_variacao_mensal(resumo_mensal: pd.DataFrame) -> dict | None:
    if resumo_mensal.empty or len(resumo_mensal) < 2:
        return None

    resumo_ordenado = resumo_mensal.sort_values(["Ano", "Mes"]).reset_index(drop=True)

    total_mes_atual = resumo_ordenado.iloc[-1]["Total"]
    total_mes_anterior = resumo_ordenado.iloc[-2]["Total"]
    variacao_absoluta = total_mes_atual - total_mes_anterior

    if total_mes_anterior != 0:
        variacao_percentual = (variacao_absoluta / total_mes_anterior) * 100
    else:
        variacao_percentual = None

    return {
        "mes_atual": total_mes_atual,
        "mes_anterior": total_mes_anterior,
        "variacao_absoluta": variacao_absoluta,
        "variacao_percentual": variacao_percentual,
    }


def calcular_variacao_anual(resumo_mensal: pd.DataFrame, ano_atual: int) -> dict | None:
    if resumo_mensal.empty:
        return None

    total_ano_atual = resumo_mensal.loc[resumo_mensal["Ano"] == ano_atual, "Total"].sum()
    total_ano_anterior = resumo_mensal.loc[resumo_mensal["Ano"] == ano_atual - 1, "Total"].sum()

    if total_ano_atual == 0 and total_ano_anterior == 0:
        return None

    variacao_absoluta = total_ano_atual - total_ano_anterior

    if total_ano_anterior != 0:
        variacao_percentual = (variacao_absoluta / total_ano_anterior) * 100
    else:
        variacao_percentual = None

    return {
        "total_ano_atual": total_ano_atual,
        "total_ano_anterior": total_ano_anterior,
        "variacao_absoluta": variacao_absoluta,
        "variacao_percentual": variacao_percentual,
    }


def calcular_media_movel(resumo_mensal: pd.DataFrame, janela: int = 3) -> pd.DataFrame:
    if resumo_mensal.empty:
        return resumo_mensal.copy()

    resumo = resumo_mensal.sort_values(["Ano", "Mes"]).reset_index(drop=True).copy()
    resumo["MediaMovel"] = resumo["Total"].rolling(window=janela).mean()

    return resumo


def montar_base_dashboard(df: pd.DataFrame) -> pd.DataFrame:
    resumo = gerar_resumo_mensal(df)

    if resumo.empty:
        return pd.DataFrame(
            columns=[
                "Ano",
                "Mes_Num",
                "Total",
                "Variacao_Mensal_%",
                "Variacao_Anual_%",
                "Media_Movel_3M",
                "Mes_Ref",
            ]
        )

    resumo = resumo.sort_values(["Ano", "Mes"]).reset_index(drop=True).copy()

    resumo["Variacao_Mensal_%"] = resumo["Total"].pct_change() * 100
    resumo["Variacao_Anual_%"] = resumo["Total"].pct_change(periods=12) * 100

    resumo = calcular_media_movel(resumo, janela=3)
    resumo["Media_Movel_3M"] = resumo["MediaMovel"]

    resumo["Mes_Num"] = resumo["Mes"]
    resumo["Mes_Ref"] = pd.to_datetime(
        dict(year=resumo["Ano"], month=resumo["Mes"], day=1)
    )

    return resumo[
        [
            "Ano",
            "Mes_Num",
            "Total",
            "Variacao_Mensal_%",
            "Variacao_Anual_%",
            "Media_Movel_3M",
            "Mes_Ref",
        ]
    ]

def calcular_resumo_divisao(df_mes: pd.DataFrame) -> dict:
    if df_mes.empty:
        return {
            "total_renato": 0,
            "total_brunna": 0,
            "diferenca": 0,
            "mensagem_base": "Está tudo equilibrado ✨",
            "valor_ajuste": 0,
            "destino": "",
        }

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

def calcular_orcamento_vs_realizado(
    df_despesas: pd.DataFrame,
    df_orcamento: pd.DataFrame,
    ano: int,
    mes: int,
) -> pd.DataFrame:
    if df_orcamento.empty:
        return pd.DataFrame(columns=["Categoria", "Orcamento", "Total", "Diferenca"])

    df_orcamento_mes = df_orcamento[
        (df_orcamento["Mes"] == mes) & (df_orcamento["Ano"] == ano)
    ].copy()

    if df_orcamento_mes.empty:
        return pd.DataFrame(columns=["Categoria", "Orcamento", "Total", "Diferenca"])

    df_gastos = (
        df_despesas.groupby("Categoria")["Total"]
        .sum()
        .reset_index()
    )

    df_comparacao = df_orcamento_mes.merge(df_gastos, on="Categoria", how="left")
    df_comparacao["Total"] = df_comparacao["Total"].fillna(0)
    df_comparacao["Diferenca"] = df_comparacao["Orcamento"] - df_comparacao["Total"]

    return df_comparacao.sort_values("Categoria").reset_index(drop=True)