import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def configurar_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def acessar_assyst(usuario, senha):
    driver = configurar_driver()
    chamados = []
    try:
        driver.get("https://portalllk.lanlink.com.br/assystweb/application.do")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(usuario)
        driver.find_element(By.ID, "password").send_keys(senha)
        driver.find_element(By.ID, "login_button").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu_chamados")))
        driver.find_element(By.ID, "menu_chamados").click()
        time.sleep(2)
        driver.find_element(By.ID, "dijit_MenuItem_73_text").click()  # Filtro 1
        time.sleep(2)
        driver.find_element(By.ID, "dijit_MenuItem_74_text").click()  # Filtro 2
        time.sleep(2)
        driver.find_element(By.ID, "components_MenuItem_21_text").click()  # Filtro Especificações
        time.sleep(2)
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
    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")
    finally:
        driver.quit()
    
    return pd.DataFrame(chamados)

def save_file(df):
    file_path = "/tmp/chamados_dezembro.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

st.title("Assyst Web - Sistema de Chamados")
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Login"):
    if usuario and senha:
        df = acessar_assyst(usuario, senha)
        if not df.empty:
            st.success("Login bem-sucedido!")
            st.dataframe(df)
            file_path = save_file(df)
            st.download_button("Baixar Relatório", file_path, file_name="chamados_dezembro.xlsx")
        else:
            st.error("Nenhum dado encontrado ou erro na consulta.")
    else:
        st.warning("Por favor, insira seu usuário e senha.")
