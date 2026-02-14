import pandas as pd


def ler_excel_despesas(arquivo):
    df = pd.read_excel(arquivo)
    colunas_esperadas = [
        "Data",
        "Descrição",
        "Categoria",
        "Valor Brunna",
        "Valor Renato",
        "Total"
    ]

    if not all(col in df.columns for col in colunas_esperadas):
        raise ValueError("O arquivo não possui as colunas esperadas.")

    return df


def ler_excel_orcamento(arquivo):
    df = pd.read_excel(arquivo)

    colunas_esperadas = [
        "Categoria",
        "Valor Orçado"
    ]

    if not all(col in df.columns for col in colunas_esperadas):
        raise ValueError("O arquivo de orçamento está fora do padrão.")

    return df
