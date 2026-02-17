from modules.historico import (
    carregar_historico,
    salvar_historico,
    remover_mes,
    CAMINHO_DESPESAS,
    CAMINHO_ORCAMENTOS
)
from modules.utils import extrair_mes_ano
import streamlit as st
import pandas as pd
import modules.upload

from modules.upload import ler_excel_despesas, ler_excel_orcamento
print(modules.upload.__file__)

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

    df_despesas = None
    df_orcamento = None

    # =============================
    # 📌 PROCESSAR DESPESAS
    # =============================
    if despesas_file is not None:
        try:
            df_despesas = ler_excel_despesas(despesas_file)

            # 🔄 Tratamentos
            df_despesas["Data"] = pd.to_datetime(df_despesas["Data"])
            df_despesas["Valor Renato"] = pd.to_numeric(
                df_despesas["Valor Renato"], errors="coerce"
            ).fillna(0)

            df_despesas["Valor Brunna"] = pd.to_numeric(
                df_despesas["Valor Brunna"], errors="coerce"
            ).fillna(0)

            df_despesas["Categoria"] = (
                df_despesas["Categoria"]
                .astype(str)
                .str.strip()
                .str.title()
            )

            df_despesas["Total"] = (
                df_despesas["Valor Renato"] +
                df_despesas["Valor Brunna"]
            )

            # 🔢 Totais
            total_geral = df_despesas["Total"].sum()
            total_renato = df_despesas["Valor Renato"].sum()
            total_brunna = df_despesas["Valor Brunna"].sum()

            col1, col2, col3 = st.columns(3)

            col1.metric("💰 Total Geral", f"R$ {total_geral:,.2f}")
            col2.metric("🧍 Total Renato", f"R$ {total_renato:,.2f}")
            col3.metric("🧍‍♀️ Total Brunna", f"R$ {total_brunna:,.2f}")

            ano_d, mes_d = extrair_mes_ano(df_despesas)
            st.success(f"Despesas detectadas: {mes_d}/{ano_d}")

            # 📋 Tabela completa
            st.subheader("📋 Gastos Detalhados")

            # 🔹 Criar cópia apenas para exibição
            df_exibicao = df_despesas.copy()
            df_exibicao["Data"] = df_exibicao["Data"].dt.strftime("%d/%m/%Y")

            df_exibicao["Valor Renato"] = df_exibicao["Valor Renato"].map(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            df_exibicao["Valor Brunna"] = df_exibicao["Valor Brunna"].map(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            df_exibicao["Total"] = df_exibicao["Total"].map(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(df_exibicao)

            # 📊 Gráfico por categoria
            import plotly.express as px

            df_categoria = (
                df_despesas
                .groupby("Categoria")["Total"]
                .sum()
                .reset_index()
                .sort_values(by="Total", ascending=False)
            )

            st.subheader("📊 Gastos por Categoria")

            fig = px.bar(
                df_categoria,
                x="Categoria",
                y="Total",
                text_auto=".2s"
            )

            fig.update_layout(
                yaxis_title="Total Gasto (R$)",
                xaxis_title="Categoria"
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao processar despesas: {e}")

    # =============================
    # 📌 PROCESSAR ORÇAMENTO
    # =============================
    if orcamento_file is not None:

        if df_despesas is None:
            st.warning("Carregue as despesas antes do orçamento.")
            st.stop()

        try:
            df_orcamento = ler_excel_orcamento(orcamento_file)

            df_orcamento["Categoria"] = (
                df_orcamento["Categoria"]
                .astype(str)
                .str.strip()
                .str.title()
            )

            df_orcamento["Orcamento"] = pd.to_numeric(
                df_orcamento["Orcamento"], errors="coerce"
            ).fillna(0)

            df_orcamento["Mes"] = pd.to_numeric(
                df_orcamento["Mes"], errors="coerce"
            ).fillna(0)

            df_orcamento["Ano"] = pd.to_numeric(
                df_orcamento["Ano"], errors="coerce"
            ).fillna(0)

            df_orcamento_mes = df_orcamento[
                (df_orcamento["Mes"] == mes_d) &
                (df_orcamento["Ano"] == ano_d)
            ]

            if df_orcamento_mes.empty:
                st.warning("Não há orçamento para este mês.")
            else:
                df_gastos = (
                    df_despesas
                    .groupby("Categoria")["Total"]
                    .sum()
                    .reset_index()
                )

                df_comparacao = df_orcamento_mes.merge(
                    df_gastos,
                    on="Categoria",
                    how="left"
                )

                df_comparacao["Total"] = df_comparacao["Total"].fillna(0)

                df_comparacao["Diferenca"] = (
                    df_comparacao["Orcamento"] -
                    df_comparacao["Total"]
                )

                st.subheader("🎯 Comparação com Orçamento")
                st.dataframe(df_comparacao)

        except Exception as e:
            st.error(f"Erro ao processar orçamento: {e}")

    # =============================
    # 📌 SALVAR HISTÓRICO
    # =============================
    if df_despesas is not None:
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
                    historico_despesas, ano_d, mes_d
                )

            historico_despesas = pd.concat(
                [historico_despesas, df_despesas]
            )

            salvar_historico(historico_despesas, CAMINHO_DESPESAS)

            st.success("Dados salvos com sucesso!")

# ==========================
# ABA DASHBOARD
# ==========================
with aba_dashboard:
    st.header("📊 Dashboard Geral")

    historico = carregar_historico(CAMINHO_DESPESAS)

    if historico.empty:
        st.info("Nenhum dado disponível.")
    else:
        historico["Data"] = pd.to_datetime(historico["Data"])
        historico["Mes"] = historico["Data"].dt.to_period(
            "M").dt.to_timestamp()
        historico["Ano"] = historico["Data"].dt.year

        # 🔹 Filtro de Ano
        anos_disponiveis = sorted(historico["Ano"].unique())
        ano_selecionado = st.selectbox("📅 Selecione o Ano", anos_disponiveis)

        # 🔹 Ordenar corretamente
        historico = historico.sort_values("Mes")

        # 🔹 Resumo mensal completo
        resumo_mensal = (
            historico
            .groupby("Mes")["Total"]
            .sum()
            .reset_index()
        )

        # 🔹 Média móvel contínua
        resumo_mensal["Media_Movel_3M"] = (
            resumo_mensal["Total"]
            .rolling(window=3, min_periods=1)
            .mean()
        )

        resumo_mensal = resumo_mensal.sort_values("Mes")

        resumo_mensal["Variacao_Mensal"] = (
            resumo_mensal["Total"]
            .diff()
        )

        resumo_mensal["Variacao_Mensal_%"] = (
            resumo_mensal["Total"]
            .pct_change() * 100
        )

        resumo_mensal["Variacao_Anual"] = (
            resumo_mensal["Total"]
            .pct_change(periods=12) * 100
        )

        # 🔹 Filtrar ano apenas para exibição
        resumo_mensal["Ano"] = resumo_mensal["Mes"].dt.year
        resumo_mensal = resumo_mensal[resumo_mensal["Ano"] == ano_selecionado]

        if resumo_mensal.empty:
            st.warning("Sem dados para esse ano.")
        else:
            # 💰 Total último mês
            linha_atual = resumo_mensal.iloc[-1]

            total_ultimo_mes = linha_atual["Total"]
            variacao_mes = linha_atual["Variacao_Mensal_%"]
            variacao_ano = linha_atual["Variacao_Anual"]

            # 🔹 Blindar NaN (ex: primeiro mês do histórico)
            if pd.isna(variacao_mes):
                variacao_mes = 0

            if pd.isna(variacao_ano):
                variacao_ano = 0

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💰 Total do Último Mês",
                f"R$ {total_ultimo_mes:,.2f}"
            )

            col2.metric(
                "📊 Variação vs mês anterior",
                f"{variacao_mes:.2f}%",
                delta=f"{variacao_mes:.2f}%",
                delta_color="inverse"  # verde quando cai, vermelho quando sobe
            )

            col3.metric(
                "📈 Variação vs mesmo mês ano anterior",
                f"{variacao_ano:.2f}%",
                delta=f"{variacao_ano:.2f}%",
                delta_color="inverse"
            )

            # 📉 Comparação com mês anterior
            if len(resumo_mensal) > 1:
                total_mes_anterior = resumo_mensal.iloc[-2]["Total"]
                variacao = total_ultimo_mes - total_mes_anterior

                st.metric(
                    "📊 Variação vs mês anterior",
                    f"R$ {total_ultimo_mes:,.2f}",
                    delta=f"R$ {variacao:,.2f}"
                )

            linha_atual = resumo_mensal.iloc[-1]
            variacao_mes = linha_atual["Variacao_Mensal_%"]
            variacao_ano = linha_atual["Variacao_Anual"]

            if pd.isna(variacao_mes):
                variacao_mes = 0

            if pd.isna(variacao_ano):
                variacao_ano = 0

            st.metric(
                "📈 Variação vs mês anterior",
                f"{variacao_mes:.2f}%",
                delta=f"{variacao_mes:.2f}%"
            )

            st.metric(
                "📊 Variação vs mesmo mês ano anterior",
                f"{variacao_ano:.2f}%",
                delta=f"{variacao_ano:.2f}%"
            )

            # 📈 Gráfico de evolução
            import plotly.express as px

            fig = px.line(
                resumo_mensal,
                x="Mes",
                y=["Total", "Media_Movel_3M"],
                labels={
                    "value": "Valor (R$)",
                    "variable": "Indicador"
                },
                markers=True
            )

            fig.update_layout(
                xaxis_title="Mês",
                yaxis_title="Total Gasto (R$)"
            )

            fig.update_xaxes(
                dtick="M1",
                tickformat="%m/%Y"
            )

            fig.update_traces(line=dict(width=3))
            fig.update_yaxes(tickprefix="R$ ")

            st.plotly_chart(fig, use_container_width=True)

            # 📊 Resumo por categoria (agora filtrado pelo ano selecionado)
            historico_filtrado = historico[historico["Ano"] == ano_selecionado]

            resumo_categoria = (
                historico_filtrado
                .groupby("Categoria")["Total"]
                .sum()
                .reset_index()
                .sort_values("Total", ascending=False)
            )

            fig_categoria = px.bar(
                resumo_categoria,
                x="Categoria",
                y="Total",
                text_auto=True
            )

            fig_categoria.update_layout(
                xaxis_title="Categoria",
                yaxis_title="Total Gasto (R$)"
            )

            fig_categoria.update_yaxes(tickprefix="R$ ")

            st.plotly_chart(fig_categoria, use_container_width=True)


# ==========================
# ABA HISTÓRICO
# ==========================
with aba_historico:
    st.header("Histórico")

    historico = carregar_historico(CAMINHO_DESPESAS)

    if historico.empty:
        st.info("Nenhum mês salvo ainda.")
    else:
        # Garantir formato correto
        historico["Data"] = pd.to_datetime(historico["Data"])
        historico["Mes"] = historico["Data"].dt.to_period("M").astype(str)

        # 🔢 Resumo mensal
        resumo_mensal = (
            historico
            .groupby("Mes")["Total"]
            .sum()
            .reset_index()
            .sort_values("Mes")
        )

        st.subheader("📊 Totais por Mês")

        st.dataframe(
            resumo_mensal.style.format({
                "Total": "R$ {:,.2f}"
            })
        )

        # 🎯 Seletor de mês
        mes_selecionado = st.selectbox(
            "Selecione o mês para visualizar detalhes",
            sorted(resumo_mensal["Mes"].unique(), reverse=True)
        )

        # 🔍 Filtrar mês escolhido
        df_mes = historico[historico["Mes"] == mes_selecionado].copy()

        total_geral = df_mes["Total"].sum()
        total_renato = df_mes["Valor Renato"].sum()
        total_brunna = df_mes["Valor Brunna"].sum()

        diferenca = total_renato - total_brunna

        if diferenca > 0:
            mensagem = f"Brunna deve R$ {abs(diferenca)/2:,.2f} para Renato"
        elif diferenca < 0:
            mensagem = f"Renato deve R$ {abs(diferenca)/2:,.2f} para Brunna"
        else:
            mensagem = "Está tudo equilibrado ✨"

        st.subheader("⚖️ Resumo do Mês")

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Total Geral", f"R$ {df_mes['Total'].sum():,.2f}")
        col2.metric("🧍 Total Renato", f"R$ {total_renato:,.2f}")
        col3.metric("🧍‍♀️ Total Brunna", f"R$ {total_brunna:,.2f}")

        st.info(mensagem)

        # Formatar data
        df_mes["Data"] = df_mes["Data"].dt.strftime("%d/%m/%Y")

        st.subheader("📋 Despesas Detalhadas")

        st.dataframe(
            df_mes.sort_values("Data", ascending=False).style.format({
                "Valor Renato": "R$ {:,.2f}",
                "Valor Brunna": "R$ {:,.2f}",
                "Total": "R$ {:,.2f}"
            })
        )
