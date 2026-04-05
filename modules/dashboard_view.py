import pandas as pd
import plotly.express as px
import streamlit as st

from modules.data_processing import (
    preparar_historico,
    filtrar_mes,
    resumo_categorias,
)
from modules.metrics_engine import montar_base_dashboard
from modules.formatters import formatar_moeda, NOMES_MESES
from modules.historico import carregar_historico, CAMINHO_DESPESAS



def render_dashboard():
    st.header("📊 Dashboard Geral")

    historico = carregar_historico(CAMINHO_DESPESAS)
    historico = preparar_historico(historico)

    if historico.empty:
        st.info("Nenhum dado disponível.")
        return

    resumo_mensal =  montar_base_dashboard(historico)

    ano_selecionado, mes_selecionado = render_filtros_dashboard(resumo_mensal)
    resumo_mes = resumo_mensal[
        (resumo_mensal["Ano"] == ano_selecionado)
        & (resumo_mensal["Mes_Num"] == mes_selecionado)
    ]

    if resumo_mes.empty:
        st.warning("Sem dados para o mês selecionado.")
        return

    linha_atual = resumo_mes.iloc[0]
    render_metricas_dashboard(linha_atual)
    render_grafico_evolucao(resumo_mensal)

    historico_mes = filtrar_mes(historico, ano_selecionado, mes_selecionado)
    render_grafico_categoria(historico_mes)



def render_filtros_dashboard(resumo_mensal: pd.DataFrame):
    col1, col2 = st.columns(2)

    anos_disponiveis = sorted(resumo_mensal["Ano"].unique())
    ano_selecionado = col1.selectbox("📅 Selecione o Ano", anos_disponiveis)

    meses_disponiveis = sorted(
        resumo_mensal.loc[resumo_mensal["Ano"] == ano_selecionado, "Mes_Num"].unique()
    )
    mes_selecionado = col2.selectbox(
        "🗓️ Selecione o Mês",
        meses_disponiveis,
        format_func=lambda x: NOMES_MESES[x],
    )

    return ano_selecionado, mes_selecionado



def render_metricas_dashboard(linha_atual: pd.Series):
    total_mes = linha_atual["Total"]
    variacao_mes = linha_atual["Variacao_Mensal_%"]
    variacao_ano = linha_atual["Variacao_Anual_%"]

    if pd.isna(variacao_mes):
        variacao_mes = 0
    if pd.isna(variacao_ano):
        variacao_ano = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total do Mês", formatar_moeda(total_mes))
    col2.metric(
        "📊 Variação vs mês anterior",
        f"{variacao_mes:.2f}%",
        delta=f"{variacao_mes:.2f}%",
        delta_color="inverse",
    )
    col3.metric(
        "📈 Variação vs mesmo mês ano anterior",
        f"{variacao_ano:.2f}%",
        delta=f"{variacao_ano:.2f}%",
        delta_color="inverse",
    )



def render_grafico_evolucao(resumo_mensal: pd.DataFrame):
    st.subheader("📈 Evolução dos Gastos")

    fig = px.line(
        resumo_mensal,
        x="Mes_Ref",
        y=["Total", "Media_Movel_3M"],
        labels={"value": "Valor (R$)", "variable": "Indicador", "Mes_Ref": "Mês"},
        markers=True,
    )
    fig.update_layout(xaxis_title="Mês", yaxis_title="Total Gasto (R$)")
    fig.update_xaxes(dtick="M1", tickformat="%m/%Y")
    fig.update_traces(line=dict(width=3))
    fig.update_yaxes(tickprefix="R$ ")

    st.plotly_chart(fig, use_container_width=True)



def render_grafico_categoria(historico_mes: pd.DataFrame):
    st.subheader("📊 Gastos por Categoria no Mês Selecionado")

    resumo_categoria = resumo_categorias(historico_mes)

    if resumo_categoria.empty:
        st.info("Sem categorias para o mês selecionado.")
        return

    fig = px.bar(
        resumo_categoria,
        x="Categoria",
        y="Total",
        text=resumo_categoria["Total"].apply(formatar_moeda),
    )
    fig.update_layout(xaxis_title="Categoria", yaxis_title="Total Gasto (R$)")
    fig.update_yaxes(tickprefix="R$ ")
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)
