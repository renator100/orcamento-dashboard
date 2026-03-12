import pandas as pd



def normalizar_colunas(colunas):
    return (
        colunas.astype(str)
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



def validar_colunas(df: pd.DataFrame, colunas_esperadas: list[str]):
    for col in colunas_esperadas:
        if col not in df.columns:
            raise ValueError(
                f"Coluna obrigatória ausente: {col}. Colunas encontradas: {df.columns.tolist()}"
            )



def ler_excel_despesas(arquivo):
    df = pd.read_excel(arquivo)
    df.columns = normalizar_colunas(df.columns)
    validar_colunas(df, ["Data", "Descricao", "Categoria", "Valor Renato", "Valor Brunna"])
    return df



def ler_excel_orcamento(arquivo):
    df = pd.read_excel(arquivo)
    df.columns = normalizar_colunas(df.columns)
    validar_colunas(df, ["Categoria", "Orcamento", "Mes", "Ano"])
    return df
