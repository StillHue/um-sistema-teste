import requests
import streamlit as st
import pandas as pd

ASSYST_API_LOGIN_URL = "https://portalllk.lanlink.com.br/assystrest/api/v1/login"
ASSYST_API_CHAMADOS_URL = "https://portalllk.lanlink.com.br/assystrest/api/v1/chamados"

def login_assyst_api(usuario, senha):
    auth_data = {
        "username": usuario,
        "password": senha
    }
    response = requests.post(ASSYST_API_LOGIN_URL, json=auth_data)
    if response.status_code == 200:
        return response.json().get("token"), True
    else:
        return None, False

def buscar_chamados(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(ASSYST_API_CHAMADOS_URL, headers=headers)
    if response.status_code == 200:
        chamados = response.json().get('chamados', [])
        return pd.DataFrame(chamados)
    return None

def main():
    st.title('Sistema de Busca de Chamados')

    st.sidebar.header("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button('Login'):
        if usuario and senha:
            token, sucesso = login_assyst_api(usuario, senha)
            if sucesso:
                st.success("Login bem-sucedido!")
                st.sidebar.header("Buscar Chamados")
                if st.sidebar.button('Buscar Chamados'):
                    df = buscar_chamados(token)
                    if df is not None and not df.empty:
                        st.write("Chamados encontrados:")
                        st.dataframe(df)
                        st.sidebar.download_button('Baixar Planilha', df.to_excel(index=False), file_name='chamados.xlsx')
                    else:
                        st.error("Nenhum chamado encontrado.")
            else:
                st.error("Login mal-sucedido. Usuário ou senha inválidos.")
        else:
            st.error("Por favor, insira seu usuário e senha.")

if __name__ == '__main__':
    main()
