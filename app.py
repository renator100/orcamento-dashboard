import streamlit as st
import pandas as pd

from modules.upload import ler_excel_despesas, ler_excel_orcamento
from modules.utils import extrair_mes_ano
from modules.historico import (
    carregar_historico,
    salvar_historico,
    remover_mes,
    CAMINHO_DESPESAS,
    CAMINHO_ORCAMENTOS
)

st.set_page_config(page_title="Orçamento Familiar", layout="wide")

st.title("📊 Orçamento Familiar 2.0")

aba_dashboard, aba_historico, aba_upload = st.tabs(
    ["Dashboard", "Histórico", "Atualização de Dados"]
)

# ==========================
# ABA UPLOAD
# ==========================
with aba_upload:
    st.header("Atualização de Dados")

    despesas_file = st.file_uploader("Upload Despesas", type=["xlsx"])
    orcamento_file = st.file_uploader("Upload Orçamento", type=["xlsx"])

    if despesas_file:
        try:
            df_despesas = ler_excel_despesas(despesas_file)
            ano_d, mes_d = extrair_mes_ano(df_despesas)
            st.success(f"Despesas detectadas: {mes_d}/{ano_d}")
        except Exception as e:
            st.error(str(e))

    if orcamento_file:
        try:
            df_orcamento = ler_excel_orcamento(orcamento_file)
            st.success("Orçamento carregado com sucesso.")
        except Exception as e:
            st.error(str(e))

    if despesas_file and orcamento_file:
        if st.button("Salvar no Histórico"):
            historico_despesas = carregar_historico(CAMINHO_DESPESAS)

            if not historico_despesas.empty:
                existe_mes = (
                    (pd.to_datetime(historico_despesas["Data"]).dt.year == ano_d) &
                    (pd.to_datetime(
                        historico_despesas["Data"]).dt.month == mes_d)
                ).any()
            else:
                existe_mes = False

            if existe_mes:
                st.warning("Já existe registro desse mês. Substituindo.")
                historico_despesas = remover_mes(
                    historico_despesas, ano_d, mes_d)

            historico_despesas = pd.concat([historico_despesas, df_despesas])
            salvar_historico(historico_despesas, CAMINHO_DESPESAS)

            st.success("Dados salvos com sucesso!")

# ==========================
# ABA DASHBOARD
# ==========================
with aba_dashboard:
    st.header("Dashboard")
    st.info("Em construção...")

# ==========================
# ABA HISTÓRICO
# ==========================
with aba_historico:
    st.header("Histórico")

    historico = carregar_historico(CAMINHO_DESPESAS)

    if historico.empty:
        st.info("Nenhum mês salvo ainda.")
    else:
        historico["Data"] = pd.to_datetime(historico["Data"])
        historico["Mes"] = historico["Data"].dt.to_period("M")
        resumo = historico.groupby("Mes")["Total"].sum().reset_index()
        st.dataframe(resumo)
