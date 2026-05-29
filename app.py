import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from num2words import num2words # Lembre-se de adicionar no requirements.txt

# --- FUNÇÃO DE FORMATAÇÃO PARA REAIS (PT-BR) ---
# Esta função garante pontos nas milhares e vírgula nos centavos (Ex: 150.000,00)
def formatar_real(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- FUNÇÃO PARA CONVERTER VALOR PARA EXTENSO DE MOEDA ---
def valor_por_extenso(valor):
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    extenso = num2words(inteiro, lang='pt_BR') + " reais"
    if centavos > 0:
        extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"
    return extenso

# 1. Banco de Dados de Custos (Baseado na tabela Dr. Fiscal)
dados_custo = {
    "limite": [70000, 150000, 300000, 450000, 600000, 850000, 1000000, 3000000],
    12: [2500.00, 2917.80, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    24: [3890.40, 5835.60, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    36: [5835.60, 8753.40, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    48: [7780.80, 11671.20, 15561.60, 19452.00, 23342.40, 31123.20, 35013.60, 38904.00],
    60: [9726.00, 14589.00, 19452.00, 24315.00, 29178.00, 38904.00, 43767.00, 48630.00]
}

def buscar_custo_interno(valor, meses_ref):
    for i, limite in enumerate(dados_custo["limite"]):
        if valor <= limite:
            return dados_custo[meses_ref][i]
    return dados_custo[meses_ref][-1]

st.set_page_config(page_title="Gerador de Propostas RPC", layout="wide")

st.title("📄 Gerador de Propostas RPC - Dr. Fiscal")

# --- LAYOUT PRINCIPAL ---
st.subheader("👤 Identificação")
col1, col2 = st.columns(2)
with col1:
    consultor = st.text_input("Consultor Responsável")
with col2:
    unidade = st.text_input("Unidade")

st.subheader("🏢 Dados do Cliente")
col3, col4 = st.columns(2)
with col3:
    razao_social = st.text_input("Razão Social")
with col4:
    cnpj = st.text_input("CNPJ")

st.subheader("💰 Parâmetros do Serviço")
col5, col6 = st.columns(2)
with col5:
    # Voltamos para o formato limpo de número, onde você digita livremente e o Python cuida dos pontos e vírgulas no PDF
    valor_credito = st.number_input("Faixa de Crédito (R$)", min_value=0.0, step=1000.0)
with col6:
    meses = st.selectbox("Quantidade de Meses do Diagnóstico", [12, 24, 36, 48, 60])

percentual = st.slider("Percentual da Unidade (%)", 0, 99, 25) / 100

col7, col8, col9 = st.columns(3)
with col7:
    parcelas = st.number_input("Quantidade de Parcelas", 1, 12, 5)
with col8:
    vencimento = st.text_input("Data do 1
