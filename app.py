import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

LOGIN_URL = "https://portalllk.lanlink.com.br/assystweb/application.do"
SECURITY_CHECK_URL = "https://portalllk.lanlink.com.br/assystweb/j_security_check"
USER_DATA_URL = "https://portalllk.lanlink.com.br/assystweb/application.do#eventsearch%2FEventSearchDelegatingDispatchAction.do?dispatch=monitorInitNoResults"

# Função para fazer login no Assyst
def login_assyst(username, password):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Acessa a página de login para obter qualquer dado necessário (ex: CSRF token)
    response = session.get(LOGIN_URL, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = None
        csrf_tag = soup.find('input', {'name': 'CSRFToken'})
        if csrf_tag:
            csrf_token = csrf_tag.get('value')

        login_data = {
            'j_username': username,
            'j_password': password,
            'CSRFToken': csrf_token if csrf_token else '',
            'login_button': 'Login'
        }

        login_response = session.post(SECURITY_CHECK_URL, data=login_data, headers=headers)
        if login_response.status_code == 200 and "Bem-vindo" in login_response.text:
            return session, True
        else:
            return None, False
    else:
        return None, False

# Função para buscar os chamados após login bem-sucedido
def buscar_chamados(session):
    response = session.get(USER_DATA_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        chamados = []  # Extrair dados dos chamados aqui, de acordo com a estrutura da página
        # Exemplo: Buscar dados de chamados
        # for chamado in soup.find_all('div', class_='chamado'):
        #     chamados.append({
        #         'numero': chamado.find('span', class_='numero').text,
        #         'descricao': chamado.find('span', class_='descricao').text
        #     })

        # Criar DataFrame com os chamados
        df = pd.DataFrame(chamados)
        return df
    else:
        return None

# Função principal para o Streamlit
def main():
    st.title('Sistema de Busca de Chamados')

    # Formulário de login
    st.sidebar.header("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")

    # Realiza login ao clicar no botão
    if st.sidebar.button('Login'):
        if usuario and senha:
            session, sucesso = login_assyst(usuario, senha)
            if sucesso:
                st.success("Login bem-sucedido!")
                # Exibe a tela de busca após o login
                st.sidebar.header("Buscar Chamados")
                if st.sidebar.button('Buscar Chamados'):
                    df = buscar_chamados(session)
                    if df is not None and not df.empty:
                        st.write("Chamados encontrados:")
                        st.dataframe(df)
                        # Botão para baixar a planilha
                        st.sidebar.download_button('Baixar Planilha', df.to_excel(index=False), file_name='chamados.xlsx')
                    else:
                        st.error("Nenhum chamado encontrado.")
            else:
                st.error("Login mal-sucedido. Usuário ou senha inválidos.")
        else:
            st.error("Por favor, insira seu usuário e senha.")

# Inicia a aplicação Streamlit
if __name__ == '__main__':
    main()
