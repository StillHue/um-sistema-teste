import requests
import streamlit as st
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import pandas as pd

LOGIN_URL = "https://portalllk.lanlink.com.br/assystweb/application.do"

def realizar_login(usuario, senha):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Iniciar uma sessão para manter cookies
    login_data = {
        'username': usuario,
        'password': senha,
        'login_button': 'Login',  # Pode ser necessário ajustar o nome do botão de login
    }
    
    # Fazer o POST para o login
    response = session.post(LOGIN_URL, data=login_data, headers=headers)

    # Verificar se o login foi bem-sucedido (isso depende do conteúdo da página após login)
    if "Bem-vindo" in response.text:  # Verificar se o texto "Bem-vindo" ou algo relacionado ao login bem-sucedido aparece
        return session
    else:
        return None

def acessar_chamados(session):
    chamados_url = "https://portalllk.lanlink.com.br/assystweb/eventsearch/monitorInitNoResults.do"  # URL onde você acessa os chamados
    response = session.get(chamados_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        chamados = []

        # Modifique conforme a estrutura do HTML
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
