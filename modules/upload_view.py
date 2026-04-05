import pandas as pd
import plotly.express as px
import streamlit as st

from modules.data_processing import preparar_despesas, preparar_orcamento
from modules.formatters import formatar_moeda
from modules.historico import carregar_historico, salvar_historico, remover_mes, CAMINHO_DESPESAS
from modules.upload import ler_excel_despesas, ler_excel_orcamento
from modules.utils import extrair_mes_ano
from modules.metrics_engine import calcular_orcamento_vs_realizado



def render_upload():
    st.header("Atualização de Dados")

    if "dados_nao_salvos" not in st.session_state:
        st.session_state["dados_nao_salvos"] = False

    if st.session_state["dados_nao_salvos"]:
        resumo = st.session_state.get("resumo_upload")

        if resumo:
            st.info(
                f"📄 Despesas de {resumo['mes']:02d}/{resumo['ano']} carregadas: "
                f"{resumo['qtd_registros']} registros prontos para salvar."
            )

        st.warning("⚠️ Esses dados ainda NÃO foram salvos no histórico.")    

    despesas_file = st.file_uploader("Upload Despesas", type=["xlsx"])
    orcamento_file = st.file_uploader("Upload Orçamento", type=["xlsx"])

    df_despesas = None
    ano_d = None
    mes_d = None

    if despesas_file is not None:
        try:
            df_despesas = preparar_despesas(ler_excel_despesas(despesas_file))
            ano_d, mes_d = extrair_mes_ano(df_despesas)
            render_resumo_upload(df_despesas, ano_d, mes_d)
            st.session_state["dados_nao_salvos"] = True
            st.session_state["resumo_upload"] = {
                "mes": mes_d,
                "ano": ano_d,
                "qtd_registros": len(df_despesas),
            }
        except Exception as e:
            st.error(f"Erro ao processar despesas: {e}")

    if orcamento_file is not None:
        if df_despesas is None or ano_d is None or mes_d is None:
            st.warning("Carregue e processe as despesas antes do orçamento.")
        else:
            try:
                df_orcamento = preparar_orcamento(ler_excel_orcamento(orcamento_file))
                render_comparacao_orcamento(df_despesas, df_orcamento, ano_d, mes_d)
            except Exception as e:
                st.error(f"Erro ao processar orçamento: {e}")

    if df_despesas is not None and st.button("Salvar no Histórico"):
        salvar_despesas_no_historico(df_despesas, ano_d, mes_d)



def render_resumo_upload(df_despesas, ano_d, mes_d):
    total_geral = df_despesas["Total"].sum()
    total_renato = df_despesas["Valor Renato"].sum()
    total_brunna = df_despesas["Valor Brunna"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Geral", formatar_moeda(total_geral))
    col2.metric("🧍 Total Renato", formatar_moeda(total_renato))
    col3.metric("🧍‍♀️ Total Brunna", formatar_moeda(total_brunna))

    st.success(f"Despesas detectadas: {mes_d:02d}/{ano_d}")

    st.subheader("📋 Gastos Detalhados")
    df_exibicao = df_despesas.copy()
    df_exibicao["Data"] = df_exibicao["Data"].dt.strftime("%d/%m/%Y")
    df_exibicao["Valor Renato"] = df_exibicao["Valor Renato"].map(formatar_moeda)
    df_exibicao["Valor Brunna"] = df_exibicao["Valor Brunna"].map(formatar_moeda)
    df_exibicao["Total"] = df_exibicao["Total"].map(formatar_moeda)
    st.dataframe(df_exibicao, use_container_width=True)

    df_categoria = (
        df_despesas.groupby("Categoria")["Total"]
        .sum()
        .reset_index()
        .sort_values(by="Total", ascending=False)
    )

    st.subheader("📊 Gastos por Categoria")
    fig = px.bar(
        df_categoria,
        x="Categoria",
        y="Total",
        text=df_categoria["Total"].apply(formatar_moeda),
    )
    fig.update_layout(yaxis_title="Total Gasto (R$)", xaxis_title="Categoria")
    fig.update_yaxes(tickprefix="R$ ")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)



def render_comparacao_orcamento(df_despesas, df_orcamento, ano_d, mes_d):
    df_comparacao = calcular_orcamento_vs_realizado(
        df_despesas, df_orcamento, ano_d, mes_d
    )

    if df_comparacao.empty:
        st.warning("Não há orçamento para este mês.")
        return
    
    st.subheader("🎯 Comparação com Orçamento")
    df_exibicao = df_comparacao.copy()
    for coluna in ["Orcamento", "Total", "Diferenca"]:
        df_exibicao[coluna] = df_exibicao[coluna].map(formatar_moeda)
    st.dataframe(df_exibicao, use_container_width=True)

def salvar_despesas_no_historico(df_despesas, ano_d, mes_d):
    historico_despesas = carregar_historico(CAMINHO_DESPESAS)

    if not historico_despesas.empty:
        datas_historico = pd.to_datetime(historico_despesas["Data"], errors="coerce")
        existe_mes = ((datas_historico.dt.year == ano_d) & (datas_historico.dt.month == mes_d)).any()
    else:
        existe_mes = False

    if existe_mes:
        st.warning("Já existe registro desse mês. Substituindo.")
        historico_despesas = remover_mes(historico_despesas, ano_d, mes_d)

    historico_despesas = pd.concat([historico_despesas, df_despesas], ignore_index=True)
    salvar_historico(historico_despesas, CAMINHO_DESPESAS)
    st.success("Dados salvos com sucesso!")
    st.session_state["dados_nao_salvos"] = False
    st.session_state["resumo_upload"] = None
