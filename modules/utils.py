import pandas as pd
from pathlib import Path
import os


def extrair_mes_ano(df):
    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    if df["Data"].isna().all():
        raise ValueError("Coluna Data inválida ou vazia.")

    mes_ano = df["Data"].dt.to_period("M").mode()[0]
    return mes_ano.year, mes_ano.month


# ================================
# 💾 SALVAMENTO SEGURO DE ARQUIVO
# ================================
def salvar_parquet_seguro(df, caminho_arquivo: str) -> None:
    caminho_final = Path(caminho_arquivo)
    caminho_temp = caminho_final.with_name(
        f"{caminho_final.stem}.tmp{caminho_final.suffix}"
    )

    try:
        df.to_parquet(caminho_temp, index=False)

        if not caminho_temp.exists():
            raise FileNotFoundError("O arquivo temporário não foi criado corretamente.")

        os.replace(caminho_temp, caminho_final)

    except Exception as e:
        if caminho_temp.exists():
            caminho_temp.unlink(missing_ok=True)
        raise RuntimeError(f"Erro ao salvar histórico com segurança: {e}")
