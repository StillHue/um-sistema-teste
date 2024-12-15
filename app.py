import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://portalllk.lanlink.com.br/assystweb/application.do"
SECURITY_CHECK_URL = "https://portalllk.lanlink.com.br/assystweb/j_security_check"  # A URL do login no Assyst
USERNAME = "seu_usuario"
PASSWORD = "sua_senha"

# Sessão que mantém os cookies durante as requisições
session = requests.Session()

# Cabeçalhos para imitar uma requisição de navegador normal
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Acessa a página de login para obter qualquer dado necessário (ex: CSRF token)
response = session.get(LOGIN_URL, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Se houver um token CSRF, busque-o na página (ajuste conforme necessário)
    csrf_token = None
    csrf_tag = soup.find('input', {'name': 'CSRFToken'})
    if csrf_tag:
        csrf_token = csrf_tag.get('value')

    # Dados para o formulário de login
    login_data = {
        'j_username': USERNAME,
        'j_password': PASSWORD,
        'CSRFToken': csrf_token if csrf_token else '',
        'login_button': 'Login'  # Ajuste conforme o botão de login no sistema
    }

    # Envia a requisição POST para o j_security_check
    login_response = session.post(SECURITY_CHECK_URL, data=login_data, headers=headers)

    if login_response.status_code == 200 and "Bem-vindo" in login_response.text:
        print("Login bem-sucedido!")
        # Aqui você pode continuar para a próxima etapa, como buscar os chamados
    else:
        print("Falha no login.")
else:
    print("Erro ao acessar a página de login.")
