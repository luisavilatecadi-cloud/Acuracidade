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
# 2. INJEÇÃO DE CSS
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
VERDE_CONTRASTE = "#2ECC71"
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
    
    [data-testid="stMetricDelta"] > div {{
        background-color: rgba(0, 0, 0, 0.2) !important;
        padding: 2px 8px !important;
        border-radius: 6px !important;
    }}
    
    [data-testid="stMetricDelta"] > div[data-is-down="false"] {{ color: {VERDE_CONTRASTE} !important; }}
    [data-testid="stMetricDelta"] svg[viewBox="0 0 24 24"] {{ fill: {VERDE_CONTRASTE} !important; }}

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
@st.cache_data(ttl=
