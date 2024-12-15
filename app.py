import requests
import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

LOGIN_URL = "https://portalllk.lanlink.com.br/assystweb/application.do"
CHAMADOS_URL = "https://portalllk.lanlink.com.br/assystweb/eventsearch/monitorInitNoResults.do"  # Ajuste conforme necessário para buscar os chamados

def realizar_login(usuario, senha):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = session.get(LOGIN_URL, headers=headers)
    
    # Verificar se obtemos a página de login corretamente
    if response.status_code != 200:
        st.error("Erro ao acessar a página de login.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    csrf_token = None
    for input_tag in soup.find_all('input'):
        if input_tag.get('name') == 'CSRFToken':  # Verificar o nome correto do token
            csrf_token = input_tag.get('value')

    if csrf_token is None:
        st.error("Não foi possível encontrar o token CSRF.")
        return None

    login_data = {
        'username': usuario,
        'password': senha,
        'login_button': 'Login',  # Verifique o nome correto do botão
        'CSRFToken': csrf_token  # Adicionar o token CSRF (se necessário)
    }

    login_response = session.post(LOGIN_URL, data=login_data, headers=headers)

    if "Bem-vindo" in login_response.text:  # Ajuste conforme o conteúdo da página pós-login
        return session
    else:
        return None

def acessar_chamados(session):
    response = session.get(CHAMADOS_URL)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        chamados = []

        for chamado in soup.find_all("div", class_="chamado"):  # Ajuste o seletor conforme necessário
            numero = chamado.find("span", class_="numero").text.strip()
            descricao = chamado.find("span", class_="descricao").text.strip()
            status = chamado.find("span", class_="status").text.strip()
            data_abertura = chamado.find("span", class_="data-abertura").text.strip()
            chamados.append({
                "Número": numero,
                "Descrição": descricao,
                "Status": status,
                "Data de Abertura": data_abertura
            })
        
        return pd.DataFrame(chamados)
    else:
        return None

def main():
    st.title("Sistema de Chamados Assyst")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Login"):
        session = realizar_login(usuario, senha)

        if session:
            st.success("Login bem-sucedido!")
            st.session_state.session = session  # Salvar sessão no estado para uso posterior
            st.button("Buscar Chamados")  # Botão para buscar dados

            if st.button("Buscar Chamados"):
                chamados_df = acessar_chamados(session)
                if chamados_df is not None:
                    st.success("Chamados encontrados!")
                    st.write(chamados_df)  # Exibir a tabela com os chamados
                    st.download_button(
                        label="Baixar planilha",
                        data=chamados_df.to_excel(index=False),
                        file_name="chamados.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Erro ao acessar os chamados.")
        else:
            st.error("Login mal-sucedido, usuário ou senha inválidos.")

if __name__ == "__main__":
    main()
