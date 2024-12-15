import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

# URL do Assyst
ASSYST_LOGIN_URL = "https://portalllk.lanlink.com.br/assystweb/application.do"
ASSYST_HOME_URL = "https://portalllk.lanlink.com.br/assystweb/application.do#main.do%3Fajax%3Dtrue%26dojo.preventCache%3D1734291729494"

def obter_token_csrf():
    session = requests.Session()
    response = session.get(ASSYST_LOGIN_URL)
    
    if response.status_code != 200:
        return None, None
    
    # Aqui vamos imprimir o HTML da página para análise
    print(response.text)  # Apenas para debug, remova depois de identificar o problema

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Tentando encontrar o CSRF token
    token = soup.find("input", {"name": "org.apache.struts.taglib.html.TOKEN"})
    if token:
        csrf_token = token['value']
        return csrf_token, session
    else:
        # Se o token não for encontrado, tente outra abordagem
        return None, None

def fazer_login(usuario, senha, session, csrf_token):
    login_data = {
        "j_username": usuario,
        "j_password": senha,
        "org.apache.struts.taglib.html.TOKEN": csrf_token
    }
    response = session.post(ASSYST_LOGIN_URL, data=login_data)
    if "Login mal-sucedido" in response.text:
        return False
    return True

def buscar_chamados(session):
    chamados_url = ASSYST_HOME_URL  # Use a URL que lista os chamados
    response = session.get(chamados_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Aqui você pode extrair os dados de chamados da página, adaptando conforme o HTML
        chamados = []  # Lista de chamados, você deve extrair da página
        return pd.DataFrame(chamados)
    return None

def main():
    st.title('Sistema de Busca de Chamados')

    st.sidebar.header("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button('Login'):
        if usuario and senha:
            csrf_token, session = obter_token_csrf()
            if csrf_token:
                login_sucesso = fazer_login(usuario, senha, session, csrf_token)
                if login_sucesso:
                    st.success("Login bem-sucedido!")
                    st.sidebar.header("Buscar Chamados")
                    if st.sidebar.button('Buscar Chamados'):
                        df = buscar_chamados(session)
                        if df is not None and not df.empty:
                            st.write("Chamados encontrados:")
                            st.dataframe(df)
                            st.sidebar.download_button('Baixar Planilha', df.to_excel(index=False), file_name='chamados.xlsx')
                        else:
                            st.error("Nenhum chamado encontrado.")
                else:
                    st.error("Login mal-sucedido. Usuário ou senha inválidos.")
            else:
                st.error("Não foi possível obter o token CSRF.")
        else:
            st.error("Por favor, insira seu usuário e senha.")

if __name__ == '__main__':
    main()
