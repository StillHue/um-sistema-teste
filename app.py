import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

def login_ao_sistema(usuario, senha):
    url_login = 'https://portalllk.lanlink.com.br/assystweb/application.do'
    session = requests.Session()
    login_data = {
        'username': usuario,
        'password': senha,
    }
    response = session.post(url_login, data=login_data)
    if response.status_code == 200:
        return session
    else:
        st.error("Falha no login. Verifique suas credenciais.")
        return None

def buscar_chamados(session, filtro):
    url = 'https://portalllk.lanlink.com.br/assystweb/chamados.do'
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        dados = []
        chamados = soup.find_all('div', class_='chamado-row')
        for chamado in chamados:
            numero = chamado.find('span', class_='numero').text.strip()
            descricao = chamado.find('span', class_='descricao').text.strip()
            status = chamado.find('span', class_='status').text.strip()
            data_abertura = chamado.find('span', class_='data-abertura').text.strip()
            dados.append([numero, descricao, status, data_abertura])
        return pd.DataFrame(dados, columns=['Número', 'Descrição', 'Status', 'Data de Abertura'])
    else:
        st.error(f"Falha ao buscar dados. Código de status: {response.status_code}")
        return pd.DataFrame()

def app():
    st.title('Sistema de Busca de Chamados')
    usuario = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')
    if st.button('Login'):
        session = login_ao_sistema(usuario, senha)
        if session:
            st.success('Login bem-sucedido!')
            filtro = st.selectbox('Escolha o filtro', ['TJRN - 1N CHAMADOS', 'TJRN - 2N CHAMADOS'])
            st.info(f'Filtro selecionado: {filtro}')
            if st.button('Buscar Chamados'):
                df = buscar_chamados(session, filtro)
                if not df.empty:
                    st.dataframe(df)
                    st.download_button(
                        label="Baixar Planilha",
                        data=df.to_excel(index=False),
                        file_name="chamados_dezembro.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.error('Não foi possível fazer login, tente novamente.')

if __name__ == '__main__':
    app()
