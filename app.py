import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

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
    try:
        driver.get("https://portalllk.lanlink.com.br/assystweb/application.do")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(usuario)
        driver.find_element(By.ID, "password").send_keys(senha)
        driver.find_element(By.ID, "login_button").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu_chamados")))

        if "menu_chamados" in [el.get_attribute('id') for el in driver.find_elements(By.TAG_NAME, "a")]:
            return True, driver
        else:
            return False, driver

    except Exception as e:
        return False, driver
    finally:
        driver.quit()

def buscar_chamados(driver):
    try:
        driver.get("https://portalllk.lanlink.com.br/assystweb/application.do#eventsearch%2FEventSearchDelegatingDispatchAction.do?dispatch=monitorInitNoResults")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dijit_MenuItem_73_text")))
        driver.find_element(By.ID, "dijit_MenuItem_73_text").click()
        time.sleep(2)
        driver.find_element(By.ID, "dijit_MenuItem_74_text").click()
        time.sleep(2)
        driver.find_element(By.ID, "components_MenuItem_21_text").click()
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
        return pd.DataFrame(chamados)
    except Exception as e:
        return None

def salvar_planilha(df):
    arquivo_destino = "chamados_dezembro.xlsx"
    df.to_excel(arquivo_destino, index=False)
    return arquivo_destino

def main():
    st.title("Sistema de Busca de Chamados")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Login"):
        sucesso, driver = acessar_assyst(usuario, senha)
        
        if sucesso:
            st.success("Login bem-sucedido!")
            st.session_state.logged_in = True
        else:
            st.error("Login mal-sucedido, usuário ou senha inválidos.")
            st.session_state.logged_in = False
    
    if st.session_state.get("logged_in", False):
        if st.button("Buscar Chamados"):
            driver = configurar_driver()
            df_chamados = buscar_chamados(driver)
            if df_chamados is not None:
                st.write(df_chamados)
                arquivo = salvar_planilha(df_chamados)
                st.download_button(
                    label="Baixar Planilha",
                    data=open(arquivo, "rb").read(),
                    file_name=arquivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("Não foi possível buscar os chamados.")
    
if __name__ == "__main__":
    main()
