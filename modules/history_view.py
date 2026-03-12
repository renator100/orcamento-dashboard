import streamlit as st

from modules.data_processing import preparar_historico, calcular_resumo_divisao
from modules.formatters import formatar_moeda
from modules.historico import carregar_historico, CAMINHO_DESPESAS



def render_historico():
    st.header("Histórico")

    historico = carregar_historico(CAMINHO_DESPESAS)
    historico = preparar_historico(historico)

    if historico.empty:
        st.info("Nenhum mês salvo ainda.")
        return

    resumo_mensal = (
        historico.groupby("Mes_Str")["Total"]
        .sum()
        .reset_index()
        .sort_values("Mes_Str")
    )

    st.subheader("📊 Totais por Mês")
    resumo_exibicao = resumo_mensal.copy()
    resumo_exibicao["Total"] = resumo_exibicao["Total"].map(formatar_moeda)
    st.dataframe(resumo_exibicao, use_container_width=True)

    mes_selecionado = st.selectbox(
        "Selecione o mês para visualizar detalhes",
        sorted(resumo_mensal["Mes_Str"].unique(), reverse=True),
    )

    df_mes = historico[historico["Mes_Str"] == mes_selecionado].copy()
    resumo_divisao = calcular_resumo_divisao(df_mes)

    st.subheader("⚖️ Resumo do Mês")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Geral", formatar_moeda(df_mes["Total"].sum()))
    col2.metric("🧍 Total Renato", formatar_moeda(resumo_divisao["total_renato"]))
    col3.metric("🧍‍♀️ Total Brunna", formatar_moeda(resumo_divisao["total_brunna"]))

    if resumo_divisao["diferenca"] == 0:
        st.info(resumo_divisao["mensagem_base"])
    else:
        st.info(
            f"{resumo_divisao['mensagem_base']} {formatar_moeda(resumo_divisao['valor_ajuste'])} para {resumo_divisao['destino']}"
        )

    st.subheader("📋 Despesas Detalhadas")
    df_exibicao = df_mes.copy()
    df_exibicao["Data"] = df_exibicao["Data"].dt.strftime("%d/%m/%Y")
    df_exibicao = df_exibicao.sort_values("Data", ascending=False)
    df_exibicao["Valor Renato"] = df_exibicao["Valor Renato"].map(formatar_moeda)
    df_exibicao["Valor Brunna"] = df_exibicao["Valor Brunna"].map(formatar_moeda)
    df_exibicao["Total"] = df_exibicao["Total"].map(formatar_moeda)
    st.dataframe(df_exibicao, use_container_width=True)
