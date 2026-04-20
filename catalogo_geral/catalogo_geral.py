import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="TECADI - Hub Acuracidade",
    page_icon="🏢",
    layout="wide"
)

# 2. Estilização Estilo "Netflix Corporativo"
st.markdown("""
    <style>
    .stApp {
        background-color: #050C16;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .logo-container { padding: 20px 0; }

    .hero-title {
        color: #009FE3; 
        font-size: 50px;
        font-weight: 700;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: white;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.8;
    }

    .category-title {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 20px;
        border-left: 4px solid #009FE3;
        padding-left: 15px;
    }

    .netflix-card {
        background-color: #0B1E33;
        border-radius: 8px;
        padding: 0px;
        transition: transform 0.4s ease, border-color 0.4s ease;
        border: 1px solid #1D569B;
        overflow: hidden;
        height: 240px;
        display: flex;
        flex-direction: column;
        position: relative; 
    }

    .full-card-link {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        text-decoration: none;
        z-index: 10;
    }

    .netflix-card:hover {
        transform: scale(1.05);
        border-color: #009FE3;
        box-shadow: 0 10px 20px rgba(0, 159, 227, 0.3);
    }

    .card-banner {
        height: 100px;
        background: linear-gradient(135deg, #133A68 0%, #1D569B 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 45px;
    }

    .card-content {
        padding: 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .card-title-text {
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .card-desc {
        color: #A0AEC0;
        font-size: 14px;
        line-height: 1.4;
    }

    .footer {
        margin-top: 80px;
        padding: 30px;
        border-top: 1px solid #1D569B;
        color: #4A5568;
        font-size: 12px;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Principal
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("https://tecadi.com.br/wp-content/uploads/2024/01/LOGO-HORIZONTAL_BRANCA_p.png.webp", width=180)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<h1 class="hero-title">Hub Acuracidade</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Gestão Fiscal e WMS • Inteligência de Dados</p>', unsafe_allow_html=True)

# 4. Grid de Dashboards (Ajustado para 2 colunas principais)
st.markdown('<p class="category-title">Dashboards Disponíveis</p>', unsafe_allow_html=True)

# Criamos 4 colunas mas usamos apenas as 2 centrais para um visual mais equilibrado
# Ou usamos apenas 2 se você quiser que eles ocupem a tela toda. 
# Abaixo usei 2 colunas diretas:
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div class="netflix-card">
            <a href="https://acuracidade-financeira.streamlit.app/" target="_blank" class="full-card-link"></a>
            <div class="card-banner">💰</div>
            <div class="card-content">
                <div class="card-title-text">Acuracidade Financeira</div>
                <div class="card-desc">Análise de Impacto Financeiro, Divergências de Valores e Auditoria de Perdas Operacionais.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="netflix-card">
            <a href="https://acuracidade-inventario-ciclico-wms.streamlit.app/" target="_blank" class="full-card-link"></a>
            <div class="card-banner">📦</div>
            <div class="card-content">
                <div class="card-title-text">Acuracidade WMS</div>
                <div class="card-desc">Indicadores de Acuracidade WMS, Acuracidade Financeira e de Execução dos Inventário Cíclicos.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 5. Rodapé
st.markdown("""
    <div class="footer">
        <b>SETOR DE ACURACIDADE - TECADI LOGÍSTICA</b><br>
        Monitoramento de performance interna e integridade de estoque.
    </div>
""", unsafe_allow_html=True)
