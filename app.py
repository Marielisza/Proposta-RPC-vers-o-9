import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# --- FUNÇÃO DE FORMATAÇÃO PARA REAIS (PT-BR) ---
def formatar_real(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
    gerar_btn = st.button("Gerar Proposta Profissional", use_container_width=True, type="primary")

if gerar_btn:
    if not razao_social or not consultor:
        st.error("Por favor, preencha a Razão Social e o Consultor.")
    else:
        # Cálculos de valores
        custo_base = buscar_custo_interno(valor_credito, meses)
        total_servico = custo_base / (1 - percentual)
        valor_parcela = total_servico / parcelas

        # ==========================================
        # GERAÇÃO DO PDF
        # ==========================================
        pdf = FPDF()
        
        # --- PÁGINA 1: CAPA VERMELHA ---
        pdf.add_page()
        
        # Puxa a sua imagem vermelha para cobrir o fundo A4 (210x297mm)
        nome_imagem_capa = 'logo_colorida.png.png'
        if os.path.exists(nome_imagem_capa):
            pdf.image(nome_imagem_capa, 0, 0, w=210, h=297)
        else:
            # Cor de segurança caso a imagem não esteja na pasta
            pdf.set_fill_color(200, 20, 30) 
            pdf.rect(0, 0, 210, 297, 'F')
        
        pdf.set_text_color(255, 255, 255) # Texto Branco
        
        # Bloco: EMPRESA
        pdf.set_y(80)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 6, "EMPRESA", ln=True, align='L')
        pdf.set_font("Arial", '', 20)
        pdf.multi_cell(0, 10, razao_social.upper(), align='L')
        
        pdf.ln(15)
        
        # Bloco: SERVIÇO
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 6, "SERVICO", ln=True, align='L')
        pdf.set_font("Arial", '', 18)
        pdf.multi_cell(0, 8, "Retificacoes Das Declaracoes\ne Compensacoes Mensais", align='L')
        
        pdf.ln(15)
        
        # Bloco: EMISSÃO
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 6, "EMISSAO", ln=True, align='L')
        pdf.set_font("Arial", '', 16)
        data_emissao = datetime.today().strftime('%d/%m/%Y')
        pdf.cell(0, 8, data_emissao, ln=True, align='L')

        # --- PÁGINA 2: CONTEÚDO TÉCNICO ---
        pdf.add_page()
        pdf.set_text_color(0, 0, 0) # Volta para o texto preto
        
        pdf.set_y(20) # Espaçamento inicial

        # 1. Contexto
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Contexto", ln=True)
        pdf.set_font("Arial", '', 11)
        texto_contexto = (
            f"A {razao_social} apos a identificacao das oportunidades apresentadas no trabalho de "
            "Diagnostico Tributario apresentado pela Dr. Fiscal, verificou que a habilitacao dos "
            "creditos de PIS e COFINS, dependem da retificacao das informacoes constantes da DCTF "
            "e EFD Contribuicoes."
        )
        pdf.multi_cell(0, 6, texto_contexto)
        pdf.ln(5)

        # 2. Objetivo
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Objetivo", ln=True)
        pdf.set_font("Arial", '', 11)
        texto_objetivo = (
            "O servico de Retificacoes e Procedimentos de Compensacao preve a retificacao de todas "
            "as obrigacoes fiscais acessorias necessarias para a correta habilitacao dos ativos "
            "identificados no trabalho de Diagnostico Tributario. Estao contempladas no escopo "
            "dessa proposta a retificacao de DCTF, EFD Contribuicoes, bem como a preparacao dos "
            "pedidos de ressarcimentos, compensacoes mensais e alem de todas as diligencias.\n\n"
            "O grande diferencial dos servicos prestados pela Dr. Fiscal atraves deste escopo e a "
            "profundidade dos exames e analises, assim como o emprego de horas tecnicas de "
            "especialistas em Declaracoes Eletronicas."
        )
        pdf.multi_cell(0, 6, texto_objetivo)
        pdf.ln(5)

        # 3. Escopo
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Escopo", ln=True)
        pdf.set_font("Arial", '', 11)
        texto_escopo = (
            "A Dr. Fiscal prestara servicos de consultoria fiscal, no sentido de retificacao das "
            "obrigacoes fiscais acessorias, de acordo com as orientacoes e regulamentacoes emitidas "
            "pela Receita Federal do Brasil, com o objetivo de habilitar eventuais ativos que a "
            "empresa tenha direito de receber."
        )
        pdf.multi_cell(0, 6, texto_escopo)
        pdf.ln(5)

        # 4. Investimento
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Investimento", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, "A seguir, descrevemos o investimento proposto para cada escopo dos trabalhos apresentados:")
        
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"a) Remuneracao: R$ {formatar_real(total_servico)} condicionado a avaliacao da proposta dentro da validade prevista nas notas desta proposta.")
        pdf.multi_cell(0, 6, f"b) Horas tecnicas alocadas: {horas_tecnicas} horas.")
        pdf.multi_cell(0, 6, f"c) Forma de Pagamento: A vista ou em ate {parcelas} parcelas mensais, iguais e consecutivas.")
        pdf.multi_cell(0, 6, f"d) Prazo para finalizacao: 60 dias.")
        pdf.ln(5)

        # 5. Notas
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Notas", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, "Esta proposta tem validade de 3 dias uteis.")

        # Rodapé
        pdf.set_y(-25)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, razao_social.upper(), ln=True, align='C')
        pdf.cell(0, 5, "PROPOSTA DE TRABALHO - Pagina 2 de 2", ln=True, align='C')

        # Download do PDF
        try:
            pdf_output = bytes(pdf.output())
        except TypeError:
            pdf_output = pdf.output(dest='S').encode('latin-1')

        st.success("Cálculo realizado e PDF gerado com sucesso!")
        st.download_button(
            label="📥 Baixar Proposta em PDF",
            data=pdf_output,
            file_name=f"Proposta_RPC_{razao_social}.pdf",
            mime="application/pdf",
            type="primary"
        )