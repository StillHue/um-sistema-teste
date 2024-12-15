import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

def autenticar_usuario(usuario, senha):
    url_login = 'https://portalllk.lanlink.com.br/assystweb/application.do'
    session = requests.Session()
    dados = {
        'username': usuario,
        'password': senha
    }
    try:
        resposta = session.post(url_login, data=dados)
        if 'application.do' not in resposta.url:
            return session
        else:
            return None
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None

def buscar_chamados(session, filtro):
    url_chamados = 'https://portalllk.lanlink.com.br/assystweb/application.do#eventsearch%2FEventSearchDelegatingDispatchAction.do?dispatch=monitorInitNoResults'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    dados = {
        'filtro': filtro
    }
    try:
        resposta = session.post(url_chamados, data=dados, headers=headers)
        if resposta.status_code == 200:
            chamados = parse_chamados(resposta.text)
            return chamados
        else:
            return None
    except Exception as e:
        print(f"Erro ao buscar chamados: {e}")
        return None

def parse_chamados(html):
    soup = BeautifulSoup(html, 'html.parser')
    chamados = []
    # Extração de dados dos chamados (ajuste conforme a estrutura HTML real)
    for chamado in soup.find_all('div', class_='chamado-item'):
        numero = chamado.find('span', class_='numero').get_text()
        descricao = chamado.find('span', class_='descricao').get_text()
        status = chamado.find('span', class_='status').get_text()
        chamados.append({
            'Número': numero,
            'Descrição': descricao,
            'Status': status
        })
    return chamados

def gerar_planilha(chamados):
    df = pd.DataFrame(chamados)
    return df

def main():
    st.title('Sistema de Chamados')

    usuario = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')

    if st.button('Login'):
        if usuario and senha:
            session = autenticar_usuario(usuario, senha)
            if session:
                st.success("Login bem-sucedido")
                filtro = st.selectbox('Escolha o filtro', ['TJRN - 1N Chamados', 'TJRN - 2N Chamados', 'Especificações'])

                if st.button('Buscar Chamados'):
                    chamados = buscar_chamados(session, filtro)
                    if chamados:
                        df = gerar_planilha(chamados)
                        st.dataframe(df)
                        st.download_button('Baixar Planilha', df.to_excel(index=False), file_name='chamados.xlsx')
                    else:
                        st.error("Erro ao buscar chamados.")
            else:
                st.error("Login mal-sucedido, usuário ou senha inválidos.")
        else:
            st.error("Digite seu usuário e senha")

if __name__ == '__main__':
    main()
