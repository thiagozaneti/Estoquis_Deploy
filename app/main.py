import streamlit as st
import requests
import pandas as pd
import time
import pywhatkit as kit
from io import BytesIO
from fpdf import FPDF

# Configuração do Streamlit
st.set_page_config(page_title="Gerenciamento de Componentes", layout="wide")

# URL da API
url_api = "http://192.168.1.141:8000/api/v1/estoque/"

# Sidebar
with st.sidebar:
    st.image(image="icon.png",width=120)
    st.title("Gerenciamento de Placas e Componentes")

# Seleção da placa
placa = st.selectbox(
    "Selecione a Placa", 
    ("", "PLACA RDVAL-1", "REPETIDORA DE SINAL DE RADIO REPV5", "PLACA REPETIDORA VLB4", "PLCOM8 CARRETEL V4")
)

if placa:
    response = requests.get(f"{url_api}{placa}")
    if response.status_code == 200:
        data = response.json().get("data", {})
        if data:
            df = pd.DataFrame.from_dict(data, orient='index')
            df.reset_index(inplace=True)
            df.rename(columns={"index": "componente"}, inplace=True)

            # Editor de dados
            edited_df = st.data_editor(
                df,
                column_config={
                    "quantidade_total a comprar": st.column_config.NumberColumn("Quantidade Total a Comprar"),
                    "quantidade": st.column_config.NumberColumn("Quantidade da PCB", disabled=True),
                    "componente": st.column_config.TextColumn("Componente", disabled=True),
                },
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic"
            )

            # Exporta Excel para disco local
            excel_filename = f"{placa}_componentes.xlsx"
            edited_df.to_excel(excel_filename, index=False)

            # Botões de download e envio
            col1, col2, col3, col4 = st.columns(4)
            container = st.container()

            with container:
                with col1:
                    with open(excel_filename, "rb") as f:
                        st.download_button(
                            label="⬇️ Baixar Excel",
                            data=f,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="excel_download_2"  # Chave única para o quarto botão de download
                        )
                with col2:
                    csv = edited_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv,
                        file_name=f"{placa}_componentes.csv",
                        mime="text/csv",
                        key="csv_download_2"  # Chave única para o quinto botão de download
                    )
                with col3:
                    # Gerar PDF em memória
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"Componentes da {placa}", ln=True, align="C")
                    pdf.ln(10)

                    for index, row in edited_df.iterrows():
                        pdf.cell(200, 10, txt=f"{row['componente']} | Quantidade PCB: {row['quantidade']} | Total a Comprar: {row['quantidade_total a comprar']}", ln=True)

                    # Exportar PDF como bytes
                    pdf_output = pdf.output(dest='S').encode('latin1')

                    st.download_button(
                        label="📄 Baixar como PDF",
                        data=pdf_output,
                        file_name=f"{placa}_componentes.pdf",
                        mime="application/pdf",
                        key="pdf_download_2"  # Chave única para o sexto botão de download
                    )
                with col4:
                    if st.button("📤 Enviar Excel via WhatsApp", key="whatsapp_button"):
                        with st.expander("Enviar via WhatsApp (Em teste)"):
                            numero = st.text_input("Número com DDD (ex: +5511999999999)", key="whatsapp_number")
                            if st.button("Enviar Agora", key="send_button"):
                                if numero:
                                    try:
                                        # Envia o arquivo via WhatsApp
                                        kit.sendwhats_image(
                                            receiver=numero,  # Número do destinatário
                                            img_path=excel_filename,  # Caminho do arquivo
                                            caption="Segue o arquivo com a lista de componentes.",  # Mensagem opcional
                                            tab_close=True  # Fecha a aba após o envio
                                        )
                                        st.success("Arquivo enviado com sucesso!")
                                    except Exception as e:
                                        st.error(f"Erro ao enviar o arquivo: {e}")
                                else:
                                    st.warning("Digite um número válido.")
        else:
            st.warning("Nenhum componente encontrado para esta placa.")
    else:
        st.error("Erro ao acessar a API")