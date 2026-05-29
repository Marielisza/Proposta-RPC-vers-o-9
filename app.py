import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from num2words import num2words # Lembre-se de adicionar no requirements.txt

# --- FUNÇÃO DE FORMATAÇÃO PARA REAIS (PT-BR) ---
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
    valor_credito = st.number_input("Faixa de Crédito (R$)", min_value=0.0, step=1000.0, format="%.2f")
with col6:
    meses = st.selectbox("Quantidade de Meses do Diagnóstico", [12, 24, 36, 48, 60])

percentual = st.slider("Percentual da Unidade (%)", 0, 99, 25) / 100

col7, col8, col9 = st.columns(3)
with col7:
    parcelas = st.number_input("Quantidade de Parcelas", 1, 12, 5)
with col8:
    vencimento = st.text_input("Data do 1º Vencimento", value=datetime.today().strftime('%d/%m/%Y'))
with col9:
    horas_tecnicas = st.number_input("Horas Técnicas (Informativo)", value=20)


# --- BARRA LATERAL (BOTÃO DE GERAÇÃO) ---
with st.sidebar:
    st.write("") 
    st.write("")
    gerar_btn = st.button("Gerar Capa da Proposta", use_container_width=True, type="primary")

if gerar_btn:
    if not razao_social or not consultor:
        st.error("Por favor, preencha a Razão Social e o Consultor.")
    else:
        # Cálculos de valores (mantidos caso precise expandir ou validar no ecrã do Streamlit)
        custo_base = buscar_custo_interno(valor_credito, meses)
        total_servico = custo_base / (1 - percentual)
        valor_parcela = total_servico / parcelas
        extenso_total = valor_por_extenso(total_servico)

        # ==========================================
        # GERAÇÃO DO PDF (APENAS CAPA)
        # ==========================================
        pdf = FPDF()
        
        # --- REGISTRO DAS FONTES ---
        try:
            pdf.add_font('Amplesoft', '', 'AmpleSoft-Regular.ttf', uni=True)
            pdf.add_font('Amplesoft', 'B', 'AmpleSoft-Bold.ttf', uni=True)
            font_pdf = 'Amplesoft'
        except:
            font_pdf = 'Arial'

        # --- PÁGINA 1: CAPA ---
        pdf.add_page()
        
        nome_imagem_capa = 'logo_colorida.png.png'
        if os.path.exists(nome_imagem_capa):
            pdf.image(nome_imagem_capa, 0, 0, w=210, h=297)
        else:
            # Fundo Vermelho caso a imagem falhe
            pdf.set_fill_color(230, 51, 18) 
            pdf.rect(0, 0, 210, 297, 'F')
        
        pdf.set_text_color(255, 255, 255) # Texto Branco
        
        # Bloco: EMPRESA
        pdf.set_y(80)
        pdf.set_font(font_pdf, 'B', 12)
        pdf.set_x(10)
        pdf.cell(190, 6, "EMPRESA", ln=True, align='L')
        pdf.set_font(font_pdf, '', 20)
        pdf.set_x(10)
        pdf.multi_cell(190, 10, razao_social.upper(), align='L')
        
        pdf.ln(15)
        
        # Bloco: SERVIÇO
        pdf.set_font(font_pdf, 'B', 12)
        pdf.set_x(10)
        pdf.cell(190, 6, "SERVIÇO", ln=True, align='L')
        pdf.set_font(font_pdf, '', 18)
        pdf.set_x(10)
        pdf.multi_cell(190, 8, "Retificações das Declarações\ne Compensações Mensais", align='L')
        
        pdf.ln(15)
        
        # Bloco: EMISSÃO
        pdf.set_font(font_pdf, 'B', 12)
        pdf.set_x(10)
        pdf.cell(190, 6, "Data", ln=True, align='L')
        pdf.set_font(font_pdf, '', 16)
        data_emissao = datetime.today().strftime('%d/%m/%Y')
        pdf.set_x(10)
        pdf.cell(190, 8, data_emissao, ln=True, align='L')

        # Download do PDF (Removida a lógica da página 2)
        try:
            pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
        except:
            pdf_output = bytes(pdf.output())

        st.success("Cálculo realizado e Capa em PDF gerada com sucesso!")
        st.download_button(
            label="📥 Baixar Capa da Proposta",
            data=pdf_output,
            file_name=f"Capa_Proposta_{razao_social}.pdf",
            mime="application/pdf",
            type="primary"
        )
