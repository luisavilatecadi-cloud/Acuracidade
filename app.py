import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Relatório Executivo TECADI", page_icon="📊", layout="wide")

# META GLOBAL
META_GLOBAL = 0.996

# ---------------------------------------------------------
# 2. INJEÇÃO DE CSS (Cores ajustadas para melhor contraste)
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
VERDE_CONTRASTE = "#2ECC71" # Novo verde para melhor leitura
VERMELHO_CONTRASTE = "#FF4B4B"

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
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL_ESCURO} 0%, {AZUL_TECADI} 100%); }}
    [data-testid="stSidebar"]::before {{
        content: ""; display: block; height: 80px; width: 80%; margin: 20px auto;
        background-image: {logo_css}; background-size: contain; background-repeat: no-repeat; background-position: center;
    }}
    span[data-baseweb="tag"] {{ background-color: {AZUL_TECADI} !important; color: white !important; }}
    [data-testid="stWidgetLabel"] p {{ color: white !important; font-weight: 600 !important; }}
    
    /* Metrics Cards */
    [data-testid="stMetric"] {{
        background-color: {AZUL_TECADI} !important;
        padding: 15px !important; border-radius: 12px !important;
    }}
    [data-testid="stMetricValue"] > div {{ color: white !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] p {{ color: #E8F1F9 !important; text-transform: uppercase !important; font-size: 0.85rem !important; }}
    
    /* AJUSTE DE CONTRASTE NOS DELTAS (VERDE E VERMELHO) */
    [data-testid="stMetricDelta"] > div {{
        background-color: rgba(0, 0, 0, 0.2) !important; /* Fundo escurecido para destacar a cor */
        padding: 2px 8px !important;
        border-radius: 6px !important;
    }}
    
    /* Cor do texto do Delta Positivo */
    [data-testid="stMetricDelta"] > div[data-is-down="false"] {{
        color: {VERDE_CONTRASTE} !important;
    }}
    /* Cor da seta do Delta Positivo */
    [data-testid="stMetricDelta"] svg[viewBox="0 0 24 24"] {{
        fill: {VERDE_CONTRASTE} !important;
    }}

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
# 3. TRATAMENTO DE DADOS
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    url = "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQDQodk6LeaMTJ--aBY5QMzCAf0z5jcWM4ry3_TQXu-lcF4?download=1"
    file_name = "download1.xlsx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_name, "wb") as f:
            f.write(response.content)
    except Exception as e:
        st.warning(f"Erro ao baixar: {e}")

    if os.path.exists(file_name):
        df = pd.read_excel(file_name, sheet_name="Base")
    else:
        return pd.DataFrame()

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Ano'] = df['Ano'].fillna(0).astype(int).astype(str)
    df['Filial'] = df['Filial'].astype(str).str.replace('.0', '', regex=False)
    
    cols_num = ['Previsto (UN)', 'Real (UN)', 'Variaçao (UN)', 'Acuracidade (UN)', 
                'Previsto (R$)', 'Real (R$)', 'Variação (R$)', 'Acuracidade (R$)']
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df[df['Previsto (R$)'] > 0]

def f_brl(v): return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
def f_un(v): return f"{v:,.0f}".replace(",", ".")
def f_pct(v): return f"{v * 100:.2f}%"

try:
    df_base = load_data()

    if df_base.empty:
        st.error("Nenhum dado encontrado.")
    else:
        # --- SIDEBAR ---
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        anos_list = sorted(df_base['Ano'].unique().tolist(), reverse=True)
        clientes_list = sorted(df_base['Cliente'].unique().tolist())
        filiais_list = sorted(df_base['Filial'].unique().tolist())

        ano_sel = st.sidebar.multiselect("ANOS", options=anos_list, placeholder="TODOS")
        cliente_sel = st.sidebar.multiselect("CLIENTE", options=clientes_list, placeholder="TODOS")
        filial_sel = st.sidebar.multiselect("FILIAL", options=filiais_list, placeholder="TODOS")

        df_f = df_base.copy()
        if ano_sel: df_f = df_f[df_f['Ano'].isin(ano_sel)]
        if cliente_sel: df_f = df_f[df_f['Cliente'].isin(cliente_sel)]
        if filial_sel: df_f = df_f[df_f['Filial'].isin(filial_sel)]

        if not df_f.empty:
            # --- CABEÇALHO ---
            st.markdown(f'<div class="dash-header"><div class="dash-title">Painel de Inventários Gerais</div><div class="dash-subtitle">Relatório Executivo de Performance e Acuracidade de Estoque</div></div>', unsafe_allow_html=True)
            
            # --- ABAS ---
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Dados Financeiros (R$)", "📦 Dados Unitários (UN)", "🛑 Prejuízos", "🧮 Calculadora"])

            with tab1:
                st.markdown("##### Performance e Variações Financeiras")
                
                acu_fin_media = df_f['Acuracidade (R$)'].mean()
                delta_fin = acu_fin_media - META_GLOBAL
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Acuracidade (R$)", f_pct(acu_fin_media), delta=f_pct(delta_fin), help="Representa o percentual médio de acerto financeiro entre o estoque fiscal e o físico. O delta indica a distância em relação à meta global de 99,60%.")
                c2.metric("Variação Líquida", f_brl(df_f['Variação (R$)'].sum()), help="Resultado final da soma de sobras (+) e faltas (-). Indica o impacto financeiro total no estoque.")
                c3.metric("Sobra Bruta (+)", f_brl(df_f[df_f['Variação (R$)'] > 0]['Variação (R$)'].sum()), help="Valor total de itens encontrados fisicamente que não constavam no sistema (Excedentes).")
                c4.metric("Falta Bruta (-)", f_brl(df_f[df_f['Variação (R$)'] < 0]['Variação (R$)'].sum()), help="Valor total de itens que constam no sistema mas não foram encontrados fisicamente (Divergências negativas).")
                
                c5, c6 = st.columns(2)
                c5.metric("Total Financeiro Previsto", f_brl(df_f['Previsto (R$)'].sum()), help="Valor total do estoque que deveria existir conforme o sistema (Base Fiscal).")
                c6.metric("Total Financeiro Realizado", f_brl(df_f['Real (R$)'].sum()), help="Valor total do estoque efetivamente contado durante os inventários.")
                
                st.markdown("---")
                g1, g2 = st.columns(2)
                
                # Gráfico Anual
                fig1 = px.bar(df_f.groupby('Ano')['Acuracidade (R$)'].mean().reset_index(), 
                             x='Ano', y='Acuracidade (R$)', text_auto='.2%', 
                             color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Financeira Anual")
                fig1.add_hline(y=META_GLOBAL, line_dash="dash", line_color="red", 
                              annotation_text=f"Meta {f_pct(META_GLOBAL)}", annotation_position="top left")
                fig1.update_yaxes(range=[0.98, 1.0], tickformat='.2%')
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                
                # Gráfico por Filial
                fig2 = px.bar(df_f.groupby('Filial')['Acuracidade (R$)'].mean().reset_index(), 
                             x='Filial', y='Acuracidade (R$)', text_auto='.2%', 
                             color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Financeira por Filial")
                fig2.add_hline(y=META_GLOBAL, line_dash="dash", line_color="red", 
                              annotation_text=f"Meta {f_pct(META_GLOBAL)}", annotation_position="top left")
                fig2.update_yaxes(range=[0.98, 1.0], tickformat='.2%')
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                
                g1.plotly_chart(fig1, use_container_width=True)
                g2.plotly_chart(fig2, use_container_width=True)

            with tab2:
                st.markdown("##### Performance e Variações Unitárias")
                acu_un_media = df_f['Acuracidade (UN)'].mean()
                delta_un = acu_un_media - META_GLOBAL

                u1, u2, u3, u4 = st.columns(4)
                u1.metric("Acuracidade (UN)", f_pct(acu_un_media), delta=f_pct(delta_un), help="Percentual de acerto baseado na quantidade física de peças (unidades), independentemente do valor unitário.")
                u2.metric("Variação Líquida (UN)", f_un(df_f['Variaçao (UN)'].sum()), help="Diferença absoluta em unidades entre o sistema e o físico (Soma de sobras e faltas em peças).")
                u3.metric("Sobra Bruta (UN)", f_un(df_f[df_f['Variaçao (UN)'] > 0]['Variaçao (UN)'].sum()), help="Quantidade total de peças encontradas a mais no estoque.")
                u4.metric("Falta Bruta (UN)", f_un(df_f[df_f['Variaçao (UN)'] < 0]['Variaçao (UN)'].sum()), help="Quantidade total de peças que faltaram no estoque.")

                u5, u6 = st.columns(2)
                u5.metric("Total Unidades Previsto", f_un(df_f['Previsto (UN)'].sum()), help="Volume total de unidades esperado em sistema.")
                u6.metric("Total Unidades Realizado", f_un(df_f['Real (UN)'].sum()), help="Volume total de unidades efetivamente contado.")

                st.markdown("---")
                gu1, gu2 = st.columns(2)
                
                # Gráfico Anual Unitário
                fig_u1 = px.bar(df_f.groupby('Ano')['Acuracidade (UN)'].mean().reset_index(), 
                                x='Ano', y='Acuracidade (UN)', text_auto='.2%', 
                                color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Unitária Anual")
                fig_u1.add_hline(y=META_GLOBAL, line_dash="dash", line_color="red", 
                                 annotation_text=f"Meta {f_pct(META_GLOBAL)}", annotation_position="top left")
                fig_u1.update_yaxes(range=[0.98, 1.0], tickformat='.2%')
                fig_u1.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                
                # Gráfico por Filial Unitário
                fig_u2 = px.bar(df_f.groupby('Filial')['Acuracidade (UN)'].mean().reset_index(), 
                                x='Filial', y='Acuracidade (UN)', text_auto='.2%', 
                                color_discrete_sequence=[AZUL_TECADI], title="Acuracidade Unitária por Filial")
                fig_u2.add_hline(y=META_GLOBAL, line_dash="dash", line_color="red", 
                                 annotation_text=f"Meta {f_pct(META_GLOBAL)}", annotation_position="top left")
                fig_u2.update_yaxes(range=[0.98, 1.0], tickformat='.2%')
                fig_u2.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis={'type': 'category'})
                
                gu1.plotly_chart(fig_u1, use_container_width=True)
                gu2.plotly_chart(fig_u2, use_container_width=True)

            with tab3:
                st.subheader("🛑 Gestão de Divergências e Performance (SLA)")
                df_f['Meta_Calc'] = pd.to_numeric(df_f.iloc[:, 11], errors='coerce').fillna(0.995)
                total_faltas = df_f[df_f['Variação (R$)'] < 0]['Variação (R$)'].sum()
                prejuizo_excedente = df_f[df_f['Acuracidade (R$)'] < df_f['Meta_Calc']]['Variação (R$)'].sum()
                df_f['Perda_Max_Permitida'] = df_f['Previsto (R$)'] * (1 - df_f['Meta_Calc'])
                total_permitido = df_f['Perda_Max_Permitida'].sum()
                save_valor = total_permitido + total_faltas 

                c_prej1, c_prej2, c_prej3 = st.columns(3)
                with c_prej1:
                    st.metric("Total de Faltas", f_brl(total_faltas), help="Soma absoluta de todos os valores negativos (faltas) identificados, sem considerar as sobras.")
                with c_prej2:
                    st.metric("Prejuízo > Meta", f_brl(prejuizo_excedente), help="Soma das faltas apenas dos clientes/inventários onde a acuracidade ficou abaixo da meta de contrato (SLA).")
                with c_prej3:
                    delta_label = "Eficiência" if save_valor >= 0 else "Déficit"
                    st.metric("Save Operacional", f_brl(save_valor), delta=delta_label, delta_color="normal" if save_valor >= 0 else "inverse", help="Diferença entre a 'Perda Permitida' em contrato e a 'Falta Real'. Valor positivo indica que a operação perdeu menos do que o limite aceitável.")

                st.markdown("---")
                st.write("**Análise Detalhada por Cliente (Faltas):**")
                df_detalhe = df_f[df_f['Variação (R$)'] < 0].copy()
                st.dataframe(
                    df_detalhe[['Cliente', 'Filial', 'Meta_Calc', 'Acuracidade (R$)', 'Variação (R$)', 'Ano']]
                    .sort_values('Variação (R$)')
                    .style.format({
                        'Meta_Calc': '{:.2%}',
                        'Acuracidade (R$)': '{:.2%}',
                        'Variação (R$)': f_brl
                    }),
                    use_container_width=True, hide_index=True
                )

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

           st.markdown("---")
            st.subheader("🔍 Base de Dados Consolidada")
            
            # Preparação do DataFrame: remove Meta_Calc e renomeia Perda_Max_Permitida
            df_display = df_f.drop(columns=['Meta_Calc']).rename(
                columns={'Perda_Max_Permitida': 'Perda Máxima SLA'}
            )

            def style_neg(v): return f'color: {"red" if v < 0 else "black"}'
            
            st.dataframe(
                df_display.style.map(style_neg, subset=['Variaçao (UN)', 'Variação (R$)'])
                .format({
                    "Previsto (UN)": f_un, 
                    "Real (UN)": f_un, 
                    "Variaçao (UN)": f_un, 
                    "Acuracidade (UN)": f_pct, 
                    "Previsto (R$)": f_brl, 
                    "Real (R$)": f_brl, 
                    "Variação (R$)": f_brl, 
                    "Acuracidade (R$)": f_pct, 
                    "Ano": lambda x: f"{x}",
                    # Formatações corrigidas com lambda para garantir o símbolo %
                    "META": lambda x: f"{x*100:.2f}%" if x <= 1 else f"{x:.2f}%",
                    "Perda Máxima SLA": lambda x: f"R$ {x:,.0f}".replace(",", ".")
                }), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.warning("Selecione filtros na sidebar.")
except Exception as e:
    st.error(f"Erro ao processar o dashboard: {e}")
