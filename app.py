import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def configurar_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service("/path/to/chromedriver"), options=options)
    return driver

def validar_login_web(usuario, senha):
    driver = configurar_driver()
    driver.get("https://portalllk.lanlink.com.br/assystweb/application.do")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)
    driver.find_element(By.ID, "login_button").click()
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu_chamados")))
        driver.quit()
        return True  # Login bem-sucedido
    except:
        driver.quit()
        return False  # Login falhou

def buscar_chamados(usuario, senha):
    driver = configurar_driver()
    driver.get("https://portalllk.lanlink.com.br/assystweb/application.do")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)
    driver.find_element(By.ID, "login_button").click()
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu_chamados")))
    driver.find_element(By.ID, "menu_chamados").click()
    time.sleep(2)
    
    chamados = []
    elementos_chamados = driver.find_elements(By.CSS_SELECTOR, ".chamado-row")
    for chamado in elementos_chamados:
        numero = chamado.find_element(By.CSS_SELECTOR, ".numero").text
        descricao = chamado.find_element(By.CSS_SELECTOR, ".descricao").text
        status = chamado.find_element(By.CSS_SELECTOR, ".status").text
        data_abertura = chamado.find_element(By.CSS_SELECTOR, ".data-abertura").text
        chamados.append({
            "Número": numero,
            "Descrição": descricao,
            "Status": status,
            "Data de Abertura": data_abertura
        })
    driver.quit()
    return pd.DataFrame(chamados)

def main():
    st.title('Sistema de Chamados')

    usuario = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')

    if st.button('Login'):
        if usuario and senha:
            if validar_login_web(usuario, senha):
                st.success("Login bem-sucedido")
                filtro = st.selectbox('Escolha o filtro', ['TJRN - 1N Chamados', 'TJRN - 2N Chamados', 'Especificações'])

                if st.button('Buscar Chamados'):
                    chamados = buscar_chamados(usuario, senha)
                    if not chamados.empty:
                        st.dataframe(chamados)
                        st.download_button('Baixar Planilha', chamados.to_excel(index=False), file_name='chamados.xlsx')
                    else:
                        st.error("Erro ao buscar chamados.")
            else:
                st.error("Login mal-sucedido, usuário ou senha inválidos.")
        else:
            st.error("Digite seu usuário e senha")

if __name__ == '__main__':
    main()
