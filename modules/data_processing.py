import pandas as pd
from unicodedata import normalize


MAPA_CATEGORIAS = {
    "SAUDE": "Saude",
    "REMEDIO": "Saude",
    "FARMACIA": "Saude",
    "IPVA": "Impostos",
    "IPTU": "Impostos",
    "IMPOSTO": "Impostos",
    "SUPERMERCADO": "Mercado",
    "MERCADO": "Mercado",
    "ALIMENTACAO": "Restaurantes",
    "IFOOD": "Restaurantes",
    "RESTAURANTE": "Restaurantes",
    "ABASTECIMENTO": "Transporte",
    "PET": "Pets",
    "HOTEL": "Viagem",
    "VIAGENS": "Viagem",
}


def limpar_texto(texto):
    if not isinstance(texto, str):
        return texto
    texto = texto.strip().upper()
    return normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")


def padronizar_categoria(categoria):
    categoria_limpa = limpar_texto(categoria)
    return MAPA_CATEGORIAS.get(categoria_limpa, categoria_limpa.title())


def preparar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor Renato"] = pd.to_numeric(df["Valor Renato"], errors="coerce").fillna(0)
    df["Valor Brunna"] = pd.to_numeric(df["Valor Brunna"], errors="coerce").fillna(0)
    df["Categoria"] = df["Categoria"].apply(padronizar_categoria)
    df["Total"] = df["Valor Renato"] + df["Valor Brunna"]
    return df


def preparar_orcamento(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Categoria"] = df["Categoria"].apply(padronizar_categoria)
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
