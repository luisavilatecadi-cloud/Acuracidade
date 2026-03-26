import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import requests # NOVO: Biblioteca para fazer o download do link

# 1. Configuração da Página
st.set_page_config(page_title="Relatório Executivo TECADI", page_icon="📊", layout="wide")

# ---------------------------------------------------------
# 2. INJEÇÃO DE CSS - PADRÃO TECADI + ESTILO CALCULADORAS
# ---------------------------------------------------------
logo_path = "logo_tecadi.png"

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

logo_base64 = get_base64_of_bin_file(logo_path)
logo_css = f"url(data:image/png;base64,{logo_base64})" if logo_base64 else "none"

AZUL_ESCURO = "#133A68"
AZUL_TECADI = "#1D569B"
TEXTO_PADRAO = "#0A2540"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; color: {TEXTO_PADRAO}; }}
    
    .dash-header {{
        border-left: 10px solid {AZUL_TECADI};
        padding-left: 20px;
        margin-top: -30px;
        margin-bottom: 30px;
    }}
    .dash-title {{ color: {AZUL_ESCURO}; font-size: 48px !important; font-weight: 800 !important; line-height: 1; }}
    .dash-subtitle {{ color: #6c757d; font-size: 18px; }}

    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL_ESCURO} 0%, {AZUL_TECADI} 100%); }}
    [data-testid="stSidebar"]::before {{
        content: ""; display: block; height: 80px; width: 80%; margin: 20px auto;
        background-image: {logo_css}; background-size: contain; background-repeat: no-repeat; background-position: center;
    }}

    span[data-baseweb="tag"] {{ background-color: {AZUL_TECADI} !important; color: white !important; }}
    [data-testid="stWidgetLabel"] p {{ color: white !important; font-weight: 600 !important; }}

    [data-testid="stMetric"] {{
        background-color: {AZUL_TECADI} !important;
        padding: 15px !important; border-radius: 12px !important;
    }}
    [data-testid="stMetricValue"] > div {{ color: white !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] p {{ color: #E8F1F9 !important; text-transform: uppercase !important; font-size: 0.85rem !important; }}
    
    .calc-card {{
        border: 2px solid #E2E8F0;
        border-radius: 15px;
        padding: 20px;
        background-color: #F8FAFC;
        height: 100%;
    }}
    .calc-header {{
        color: {AZUL_ESCURO};
        font-weight: 800;
        font-size: 16px;
        margin-bottom: 15px;
        border-bottom: 2px solid {AZUL_TECADI};
        padding-bottom: 5px;
    }}
    
    h1, h2, h3, h4 {{ color: {AZUL_ESCURO} !important; }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. TRATAMENTO DE DADOS (ATUALIZADO PARA DOWNLOAD)
# ---------------------------------------------------------
# Cache de 600 segundos (10 minutos) para não travar o dashboard ao usar filtros
@st.cache_data(ttl=600)
def load_data():
    # URL modificada para forçar o download direto
    url = "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQDQodk6LeaMTJ--aBY5QMzCAf0z5jcWM4ry3_TQXu-lcF4?download=1"
    file_name = "download1.xlsx"
    
    try:
        # Baixa o arquivo do SharePoint
        response = requests.get(url)
        response.raise_for_status() # Garante que o download foi um sucesso
        
        # Salva o arquivo localmente como download1.xlsx
        with open(file_name, "wb") as f:
            f.write(response.content)
    except Exception as e:
        st.warning(f"Não foi possível atualizar o arquivo online. Usando a última versão local. Erro: {e}")

    # Lê o arquivo recém baixado (ou o antigo, caso o download tenha falhado)
    if os.path.exists(file_name):
        df = pd.read_excel(file_name, sheet_name="Base")
    else:
        # Fallback caso seja a primeira vez e não tenha internet/acesso
        df = pd.DataFrame() 
        return df

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Ano'] = df['Ano'].fillna(0).astype(int).astype(str)
    df['Filial'] = df['Filial'].astype(str).str.replace('.0', '', regex=False)
    
    # Converter para numérico
    cols_num = ['Previsto (UN)', 'Real (UN)', 'Variaçao (UN)', 'Acuracidade (UN)', 
                'Previsto (R$)', 'Real (R$)', 'Variação (R$)', 'Acuracidade (R$)']
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df[df['Previsto (R$)'] > 0]

def f_brl(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def f_un(v): return f"{v:,.0f}".replace(",", ".")
def f_pct(v): return f"{v * 100:.2f}%"

try:
    df_base = load_data()

    if df_base.empty:
        st.error("Nenhum dado encontrado ou falha ao carregar a base 'download1.xlsx'.")
    else:
        # --- SIDEBAR ---
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        anos_list = sorted(df_base['Ano'].unique().tolist(), reverse=True)
        clientes_list = sorted(df_base['Cliente'].unique().tolist())
        filiais_list = sorted(df_base['Filial'].unique().tolist())

        ano_sel = st.sidebar.multiselect("ANOS", options=anos_list, placeholder="TODOS")
        cliente_sel = st.sidebar.multiselect("CLIENTE", options=clientes_list, placeholder="TODOS")
        filial_sel = st.sidebar.multiselect("FILIAL", options=filiais_list, placeholder="TODOS")

        # Filtro Dinâmico
        df_f = df_base.copy()
        if ano_sel: df_f = df_f[df_f['Ano'].isin(ano_sel)]
        if cliente_sel: df_f = df_f[df_f['Cliente'].isin(cliente_sel)]
        if filial_sel: df_f = df_f[df_f['Filial'].isin(filial_sel)]

        if not df_f.empty:
            # --- CABEÇALHO ---
            col_tit, col_logo_cli = st.columns([3, 1])
            with col_tit:
                st.markdown(f'<div class="dash-header"><div class="dash-title">Painel de Inventários Gerais</div><div class="dash-subtitle">Relatório Executivo de Performance e Acuracidade de Estoque</div></div>', unsafe_allow_html=True)
            with col_logo_cli:
                if cliente_sel and len(cliente_sel) == 1:
                    nome_cli = cliente_sel[0]
                    possiveis_caminhos = [f"{nome_cli}.png", f"{nome_cli}.jpg", f"{nome_cli}.jpeg"]
                    for caminho in possiveis_caminhos:
                        if os.path.exists(caminho):
                            base64_cli = get_base64_of_bin_file(caminho)
                            st.markdown(f'<div style="display: flex; justify-content: flex-end; align-items: center; height: 100px;"><img src="data:image/png;base64,{base64_cli}" style="max-height: 90px; max-width: 100%; object-fit: contain;"></div>', unsafe_allow_html=True)
                            break

            # --- ABAS ---
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Dados Financeiros (R$)", "📦 Dados Unitários (UN)", "🛑 Prejuízos", "🧮 Calculadora"])

            with tab1:
                st.markdown("##### Performance e Variações Financeiras")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Acuracidade (R$)", f_pct(df_f['Acuracidade (R$)'].mean()))
                c2.metric("Variação Líquida", f_brl(df_f['Variação (R$)'].sum()))
                c3.metric("Sobra Bruta (+)", f_brl(df_f[df_f['Variação (R$)'] > 0]['Variação (R$)'].sum()))
                c4.metric("Falta Bruta (-)", f_brl(df_f[df_f['Variação (R$)'] < 0]['Variação (R$)'].sum()))
                c5, c6 = st.columns(2)
                c5.metric("Total Financeiro Previsto", f_brl(df_f['Previsto (R$)'].sum()))
                c6.metric("Total Financeiro Realizado", f_brl(df_f['Real (R$)'].sum()))

                g1, g2 = st.columns(2)
                # Gráfico 1 - Ano
                fig1 = px.bar(df_f.groupby('Ano')['Acuracidade (R$)'].mean().reset_index(), x='Ano', y='Acuracidade (R$)', text_auto='.2%', color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Financeira Anual")
                fig1.update_layout(yaxis_tickformat='.0%', plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                g1.plotly_chart(fig1, use_container_width=True)
                
                # Gráfico 2 - Filial
                fig2 = px.bar(df_f.groupby('Filial')['Acuracidade (R$)'].mean().reset_index(), x='Filial', y='Acuracidade (R$)', text_auto='.2%', color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Financeira por Filial")
                fig2.update_layout(yaxis_tickformat='.0%', plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                g2.plotly_chart(fig2, use_container_width=True)
                
                # Gráfico 3 - Estoque Previsto
                fig3 = px.bar(df_f.groupby('Filial')['Previsto (R$)'].sum().sort_values(ascending=False).reset_index(), x='Filial', y='Previsto (R$)', text_auto=True, color_discrete_sequence=[AZUL_ESCURO], title="Estoque Financeiro Previsto por Filial")
                fig3.update_layout(xaxis={'type': 'category'})
                st.plotly_chart(fig3, use_container_width=True)

            with tab2:
                st.markdown("##### Performance e Variações Unitárias")
                u1, u2, u3, u4 = st.columns(4)
                u1.metric("Acuracidade (UN)", f_pct(df_f['Acuracidade (UN)'].mean()))
                u2.metric("Variação Líquida (UN)", f_un(df_f['Variaçao (UN)'].sum()))
                u3.metric("Sobra Bruta (UN)", f_un(df_f[df_f['Variaçao (UN)'] > 0]['Variaçao (UN)'].sum()))
                u4.metric("Falta Bruta (UN)", f_un(df_f[df_f['Variaçao (UN)'] < 0]['Variaçao (UN)'].sum()))
                u5, u6 = st.columns(2)
                u5.metric("Total Unidades Previsto", f_un(df_f['Previsto (UN)'].sum()))
                u6.metric("Total Unidades Realizado", f_un(df_f['Real (UN)'].sum()))

                gu1, gu2 = st.columns(2)
                fig_u1 = px.bar(df_f.groupby('Ano')['Acuracidade (UN)'].mean().reset_index(), x='Ano', y='Acuracidade (UN)', text_auto='.2%', color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Unitária Anual")
                fig_u1.update_layout(yaxis_tickformat='.0%', plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                gu1.plotly_chart(fig_u1, use_container_width=True)
                
                fig_u2 = px.bar(df_f.groupby('Filial')['Acuracidade (UN)'].mean().reset_index(), x='Filial', y='Acuracidade (UN)', text_auto='.2%', color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Unitária por Filial")
                fig_u2.update_layout(yaxis_tickformat='.0%', plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                gu2.plotly_chart(fig_u2, use_container_width=True)

                fig_u3 = px.bar(df_f.groupby('Filial')['Previsto (UN)'].sum().sort_values(ascending=False).reset_index(), x='Filial', y='Previsto (UN)', text_auto=True, color_discrete_sequence=[AZUL_ESCURO], title="Estoque Unitário Previsto por Filial")
                fig_u3.update_layout(xaxis={'type': 'category'})
                st.plotly_chart(fig_u3, use_container_width=True)

            with tab3:
                st.subheader("🛑 Gestão de Divergências (Faltas)")
                df_prejuizos = df_f[df_f['Variação (R$)'] < 0].sort_values('Variação (R$)')
                st.dataframe(df_prejuizos[['Ano', 'Filial', 'Cliente', 'Variação (R$)', 'Variaçao (UN)']].style.format({"Variação (R$)": f_brl, "Variaçao (UN)": f_un}), use_container_width=True, hide_index=True)

            with tab4:
                st.subheader("🧮 Simuladores Rápidos")
                col_calc1, col_calc2 = st.columns(2)
                
                with col_calc1:
                    st.markdown('<div class="calc-card"><div class="calc-header">🎯 PREJUÍZO MÁXIMO (SLA)</div>', unsafe_allow_html=True)
                    v_calc = st.number_input("Estoque Fiscal (R$)", value=1000000.0, key="v1")
                    m_calc = st.slider("Meta de Acuracidade (%)", 90.0, 100.0, 99.5, key="m1")
                    st.metric("Limite de Perda Permitida", f_brl(v_calc * (1 - m_calc/100)))
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_calc2:
                    st.markdown('<div class="calc-card"><div class="calc-header">📊 ACURACIDADE REAL</div>', unsafe_allow_html=True)
                    v_real_c = st.number_input("Valor Realizado (R$)", value=980000.0, key="v_real_c")
                    v_prej_c = st.number_input("Soma das Faltas (R$)", value=20000.0, key="v_prej_c")
                    res_acu = (v_real_c / (v_real_c + v_prej_c)) if (v_real_c + v_prej_c) > 0 else 0
                    st.metric("Indicador Calculado", f_pct(res_acu))
                    st.markdown('</div>', unsafe_allow_html=True)

            # --- BASE FINAL ---
            st.markdown("---")
            st.subheader("🔍 Base de Dados Consolidada")
            def style_neg(v): return f'color: {"red" if v < 0 else "black"}'
            st.dataframe(df_f.style.applymap(style_neg, subset=['Variaçao (UN)', 'Variação (R$)']).format({"Previsto (UN)": f_un, "Real (UN)": f_un, "Variaçao (UN)": f_un, "Acuracidade (UN)": f_pct, "Previsto (R$)": f_brl, "Real (R$)": f_brl, "Variação (R$)": f_brl, "Acuracidade (R$)": f_pct, "Ano": lambda x: f"{x}"}), use_container_width=True, hide_index=True)

        else:
            st.warning("Selecione filtros na sidebar ou deixe-os vazios para ver 'TODOS'.")
except Exception as e:
    st.error(f"Erro ao processar o dashboard: {e}")