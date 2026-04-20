import streamlit as st
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="TECADI - Dashboard de Inventário", page_icon="📊", layout="wide")

# 2. ESTILO TECADI
AZUL_ESCURO, AZUL_TECADI, AZUL_MEDIO, CINZA_FUNDO, LARANJA_META = "#133A68", "#1D569B", "#3B82F6", "#F8FAFC", "#FF4B4B"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    .dash-header {{ border-left: 10px solid {AZUL_TECADI}; padding-left: 20px; margin-bottom: 20px; }}
    .dash-title {{ color: {AZUL_ESCURO}; font-size: 32px !important; font-weight: 800 !important; }}
    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL_ESCURO} 0%, {AZUL_TECADI} 100%); }}
    </style>
""", unsafe_allow_html=True)

def format_pct(v, is_execucao=False):
    if v >= 1.0 and not is_execucao: return "100.00%"
    if v > 0.9999 and v < 1.0 and not is_execucao: return "99.99%"
    return f"{v*100:.2f}%"

@st.cache_data(ttl=10)
def load_all_data():
    urls = {
        "U103": "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQD0njYMHEyNRZxqukJFdMnYAd8VCQnwAfBAjWcJqPjUezk?download=1",
        "U107": "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQDy2RBLtnaCRLX86MuZMvLvAbJo2YgsOLc3poDFg6qpY4Q?download=1",
        "U108": "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQBeu9gxPOzeQrumIHeBjgw6AThuAuvg10kcb9OGcPRvHEk?download=1"
    }
    dataframes = []
    unidades_nomes = {103: "103-Salseiros", 107: "107-Itaipava", 108: "108-Navegantes"}
    try:
        for unit in ["U103", "U107", "U108"]:
            resp = requests.get(urls[unit])
            df = pd.read_excel(BytesIO(resp.content), engine='openpyxl').rename(columns={'Fililal': 'Filial'})
            df['Filial_Nome'] = df['Filial'].map(unidades_nomes)
            df['Resultado (%)'] = pd.to_numeric(df['Resultado (%)'], errors='coerce').fillna(0)
            dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True), None
    except Exception as e: return None, str(e)

df_base, erro = load_all_data()

if not erro:
    meses_ordem = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
    
    with st.sidebar:
        st.image("https://tecadi.com.br/wp-content/uploads/2024/01/LOGO-HORIZONTAL_BRANCA_p.png.webp", width=200)
        
        # CSS para forçar a cor branca no label do selectbox
        st.markdown("""
            <style>
                /* Altera a cor do label de todos os widgets na sidebar para branco */
                [data-testid="stSidebar"] label {
                    color: white !important;
                    font-weight: 500;
                }
            </style>
        """, unsafe_allow_html=True)

        anos_lista = sorted([int(a) for a in df_base['Ano'].unique() if a > 0], reverse=True)
        ano_sel = st.selectbox("📅 ANO SELECIONADO", anos_lista, index=0)
        
        st.markdown("---")
        st.markdown("""
            <div style="color: white; opacity: 0.8; font-size: 0.85rem; font-style: italic;">
                💡 Use os filtros acima para atualizar todos os indicadores do dashboard.
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="dash-header"><div class="dash-title">TECADI - Painel de Controle de Inventário {ano_sel}</div></div>', unsafe_allow_html=True)
    tabs = st.tabs(["📦 Acuracidade WMS", "💰 Acuracidade Financeira", "📈 Execução Cíclico"    ])

    # Configurações de Meta, Filtro e Limite de Régua por Aba
    config_abas = {
        "wms": {"indicador": "WMS", "meta": 0.97, "min_y": 0.0},
        "fin": {"indicador": "Financeira", "meta": 0.996, "min_y": 0.5},
        "exec": {"indicador": "Execução", "meta": 1.00, "min_y": 0.0},
        "patio": {"indicador": "Pátio", "meta": 0.975, "min_y": 0.0}
    }

    def render_aba_padrao(aba_key):
        cfg = config_abas[aba_key]
        is_aba_exec = (aba_key == "exec")
        
        df_ind = df_base[df_base['Indicador'].str.contains(cfg["indicador"], na=False)]
            
        df_ano = df_ind[(df_ind['Ano'] == ano_sel) & (df_ind['Resultado (%)'] > 0)].copy()
        df_ant = df_ind[(df_ind['Ano'] == (ano_sel - 1)) & (df_ind['Resultado (%)'] > 0)].copy()
        
        st.info(f"💡 Indicadores anuais de **{ano_sel}**")

        if is_aba_exec:
            # --- ABA 3: LAYOUT ESPECIAL ---
            mes_atual_idx = datetime.now().month - 1
            mes_atual = meses_ordem[mes_atual_idx]
            mes_anterior = meses_ordem[mes_atual_idx - 1] if mes_atual_idx > 0 else "DEZ"
            
            c1, c2 = st.columns(2)
            for col, mes_ref, titulo in zip([c1, c2], [mes_anterior, mes_atual], [f"Execução {mes_anterior} (Anterior)", f"Execução {mes_atual} (Atual)"]):
                df_mes = df_ano[df_ano['Mês'] == mes_ref].groupby('Cliente')['Resultado (%)'].mean().reset_index().sort_values('Resultado (%)', ascending=False)
                
                if not df_mes.empty:
                    fig = px.bar(df_mes, x='Cliente', y='Resultado (%)', title=titulo, color_discrete_sequence=[AZUL_TECADI])
                    fig.add_hline(y=1.0, line_dash="dash", line_color=LARANJA_META, annotation_text="Meta 100%")
                    fig.update_traces(texttemplate='%{y:.2%}', textposition='inside', textfont=dict(size=14))
                    
                    fig.update_layout(
                        height=450, 
                        yaxis=dict(tickformat='.1%'), 
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    col.plotly_chart(fig, use_container_width=True)
                else:
                    col.warning(f"Sem dados para {mes_ref}")
        else:
            # --- ABAS 1 E 2: GRÁFICOS PADRÃO ---
            df_uni = df_ano.groupby(['Mês', 'Filial_Nome'], sort=False)['Resultado (%)'].mean().reset_index()
            fig_uni = px.bar(df_uni, x='Mês', y='Resultado (%)', color='Filial_Nome', barmode='group',
                             color_discrete_map={"103-Salseiros": AZUL_ESCURO, "107-Itaipava": AZUL_TECADI, "108-Navegantes": AZUL_MEDIO},
                             title="Performance Mensal por Unidade")
            
            fig_uni.update_xaxes(categoryorder='array', categoryarray=meses_ordem, range=[-0.5, 11.5])
            fig_uni.add_hline(y=cfg["meta"], line_dash="dash", line_color=LARANJA_META, annotation_text=f"Meta {cfg['meta']*100:.1f}%")
            fig_uni.update_traces(texttemplate='%{y:.2%}', textposition='inside', textangle=-90, textfont=dict(color="white"))
            fig_uni.update_layout(yaxis=dict(range=[cfg["min_y"], 1.05], tickformat='.1%'), height=500, 
                                  margin=dict(l=20, r=20, t=50, b=20), legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
            st.plotly_chart(fig_uni, use_container_width=True)

            m_ant = df_ant['Resultado (%)'].mean() if not df_ant.empty else 0
            m_atu = df_ano['Resultado (%)'].mean() if not df_ano.empty else 0
            df_cli = df_ano.groupby('Cliente')['Resultado (%)'].mean().reset_index().sort_values('Resultado (%)', ascending=False)
            
            labels = [f"Média {ano_sel-1}", f"Média {ano_sel}", " "] + df_cli['Cliente'].tolist()
            valores = [m_ant, m_atu, 0] + df_cli['Resultado (%)'].tolist()
            cores = ["#94A3B8", AZUL_ESCURO, "rgba(0,0,0,0)"] + [AZUL_TECADI] * len(df_cli)
            
            fig_cli = go.Figure(go.Bar(x=labels, y=valores, marker_color=cores,
                                       text=[f"<b>{format_pct(v, is_aba_exec)}</b>" if v > 0 else "" for v in valores],
                                       textposition='inside', textangle=-90, textfont=dict(color="white", size=14)))
            
            fig_cli.add_hline(y=cfg["meta"], line_dash="dash", line_color=LARANJA_META)
            fig_cli.update_layout(title="Média Anual por Cliente vs Médias Históricas", yaxis=dict(range=[cfg["min_y"], 1.05], tickformat='.1%'),
                                  height=500, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_cli, use_container_width=True)

        st.markdown("---")
        filiais = ["103-Salseiros", "107-Itaipava", "108-Navegantes"]
        for fil in filiais:
            df_filial = df_ano[df_ano['Filial_Nome'] == fil]
            if df_filial.empty: continue
            st.markdown(f"#### 📊 Detalhado por Cliente - {fil} ({ano_sel})")
            clientes = sorted(df_filial['Cliente'].unique())
            cols = st.columns(4)
            for idx, cliente in enumerate(clientes):
                df_c = df_filial[df_filial['Cliente'] == cliente].groupby('Mês', sort=False)['Resultado (%)'].mean().reindex(meses_ordem).reset_index()
                f_mini = go.Figure(go.Bar(x=df_c['Mês'], y=df_c['Resultado (%)'], marker_color=AZUL_ESCURO,
                                          text=[f"<b>{format_pct(v, is_aba_exec)}</b>" if v > 0 else "" for v in df_c['Resultado (%)']],
                                          textposition='inside', textangle=-90, textfont=dict(size=11)))
                f_mini.add_hline(y=cfg["meta"], line_dash="dash", line_color=LARANJA_META)
                f_mini.update_layout(title=f"<b>{cliente}</b>", yaxis=dict(range=[cfg["min_y"], 1.05] if not is_aba_exec else None, visible=False), 
                                     height=230, margin=dict(l=5, r=5, t=30, b=5), showlegend=False)
                cols[idx % 4].plotly_chart(f_mini, use_container_width=True, key=f"h_{aba_key}_{idx}_{fil}")

    def render_aba_patio():
        cfg = config_abas["patio"]
        df_patio = df_base[df_base['Indicador'].str.contains("Pátio", na=False)]
        df_ano = df_patio[df_patio['Ano'] == ano_sel].copy()

        if df_ano.empty:
            st.warning("Sem dados de Pátio para o ano selecionado.")
            return

        st.info(f"💡 Monitoramento de Pátio - **{ano_sel}**")

        # --- LINHA 1: MENSAL ---
        c1, c2 = st.columns(2)
        with c1:
            df_m = df_ano.groupby('Mês', sort=False)['Resultado (%)'].mean().reset_index()
            fig1 = px.bar(df_m, x='Mês', y='Resultado (%)', title="Acuracidade de Contêineres por Amostragem", 
                          color_discrete_sequence=[AZUL_ESCURO])
            fig1.add_hline(y=cfg["meta"], line_dash="dash", line_color=LARANJA_META, annotation_text=f"Meta {cfg['meta']*100}%")
            fig1.update_xaxes(categoryorder='array', categoryarray=meses_ordem)
            fig1.update_layout(yaxis=dict(tickformat='.1%', range=[0.9, 1.01]), height=400)
            fig1.update_traces(texttemplate='%{y:.2%}', textposition='inside')
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            # Agrupa por CORRETO e DIVERGENTE (Requer colunas Qtd_Correto e Qtd_Divergente)
            df_v = df_ano.groupby('Mês', sort=False)[['Qtd_Correto', 'Qtd_Divergente']].sum().reset_index()
            fig2 = go.Figure(data=[
                go.Bar(name='CORRETO', x=df_v['Mês'], y=df_v['Qtd_Correto'], marker_color=AZUL_ESCURO, text=df_v['Qtd_Correto'], textposition='auto'),
                go.Bar(name='DIVERGENTE', x=df_v['Mês'], y=df_v['Qtd_Divergente'], marker_color="#E67E22", text=df_v['Qtd_Divergente'], textposition='auto')
            ])
            fig2.update_layout(barmode='group', title="Contêineres Verificados Mensalmente", height=400, xaxis={'categoryorder':'array', 'categoryarray':meses_ordem})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        
        # --- LINHA 2: DIÁRIO ---
        c3, c4 = st.columns(2)
        with c3:
            # Gráfico Diário (últimos 15 registros por data)
            df_dia = df_ano.groupby('Data', sort=False)['Resultado (%)'].mean().reset_index().tail(15)
            fig3 = px.bar(df_dia, x='Data', y='Resultado (%)', title="Acuracidade Diária de Contêineres", color_discrete_sequence=[AZUL_TECADI])
            fig3.update_layout(yaxis=dict(tickformat='.1%', range=[0.9, 1.01]), height=400)
            fig3.update_traces(texttemplate='%{y:.1%}', textposition='inside')
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            df_vd = df_ano.groupby('Data', sort=False)[['Qtd_Correto', 'Qtd_Divergente']].sum().reset_index().tail(15)
            fig4 = go.Figure(data=[
                go.Bar(name='CORRETO', x=df_vd['Data'], y=df_vd['Qtd_Correto'], marker_color=AZUL_ESCURO, text=df_vd['Qtd_Correto'], textposition='auto'),
                go.Bar(name='DIVERGENTE', x=df_vd['Data'], y=df_vd['Qtd_Divergente'], marker_color="#E67E22", text=df_vd['Qtd_Divergente'], textposition='auto')
            ])
            fig4.update_layout(barmode='group', title="Contêineres Verificados Diariamente", height=400)
            st.plotly_chart(fig4, use_container_width=True)

    # Renderização das Abas
    with tabs[0]: render_aba_padrao("wms")
    with tabs[1]: render_aba_padrao("fin")
    with tabs[2]: render_aba_padrao("exec")
   

else:
    st.error(f"Erro: {erro}")
