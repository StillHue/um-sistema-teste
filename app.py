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
    url_filtro = 'https://portalllk.lanlink.com.br/assystweb/application.do#eventsearch%2FEventSearchDelegatingDispatchAction.do?dispatch=monitorInitNoResults'
    response = session.get(url_filtro)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        dados = []

        if filtro == "TJRN - 1N CHAMADOS":
            chamados = soup.find_all('div', class_='chamado-row')  # Ajuste conforme o filtro
        elif filtro == "TJRN - 2N CHAMADOS":
            chamados = soup.find_all('div', class_='chamado-row')  # Ajuste conforme o filtro
        else:
            chamados = []  # Ajuste caso o filtro não seja válido

        for chamado in chamados:
            numero = chamado.find('span', class_='numero')
            descricao = chamado.find('span', class_='descricao')
            status = chamado.find('span', class_='status')
            data_abertura = chamado.find('span', class_='data-abertura')

            if numero and descricao and status and data_abertura:
                dados.append([
                    numero.text.strip(),
                    descricao.text.strip(),
                    status.text.strip(),
                    data_abertura.text.strip()
                ])
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
