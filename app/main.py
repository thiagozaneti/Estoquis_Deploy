import streamlit as st
import requests
url_api = "http://192.168.1.12:8000/api/v1/estoque/"

with st.sidebar:
    st.title("Sistema para gerenciamento e criação de relação de placas")

if st.button("Placa PLACA RDVAL1"):
    response = requests.get(url_api)
    if response.status_code == 200:
        data = response.json()
        st.json(data)