import pandas as pd


def ler_excel_despesas(arquivo):
    df = pd.read_excel(arquivo)

    # 🔹 Normalizar nomes das colunas
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("ç", "c")
        .str.replace("ã", "a")
        .str.replace("á", "a")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
        .str.replace("Descrição", "Descricao")
    )

    colunas_esperadas = [
        "Data",
        "Descricao",
        "Categoria",
        "Valor Renato",
        "Valor Brunna",
    ]

    for col in colunas_esperadas:
        if col not in df.columns:
            raise ValueError(
                f"Coluna obrigatória ausente: {col}. "
                f"Colunas encontradas: {df.columns.tolist()}"
            )

    return df


def ler_excel_orcamento(arquivo):
    df = pd.read_excel(arquivo)

    # Normalizar nomes das colunas
    df.columns = df.columns.str.strip()

    print("COLUNAS NORMALIZADAS:", df.columns.tolist())

    colunas_esperadas = ["Categoria", "Orcamento", "Mes", "Ano"]

    for col in colunas_esperadas:
        if col not in df.columns:
            raise ValueError(
                f"Coluna obrigatória ausente: {col}. "
                f"Colunas encontradas: {df.columns.tolist()}"
            )

    return df
