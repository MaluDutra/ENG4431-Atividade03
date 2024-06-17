from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import requests as req
import json
from datetime import datetime, timezone

#Funções
def menu():
  print('\n\n')
  print('='*90)
  print("\nBoas Vindas ao programa sobre Studio Ghibli!!\n")
  print("Escolha uma das opções abaixo:")
  print("1 - Consultar sinopse de um filme") 
  print("2 - Entrar na conta do site do Studio Ghibli")
  print("3 - Cadastrar conta no site Studio Ghibli")
  print("4 - Consultar nota do filme no site IMDb") 
  print("5 - Sair\n")
  print('='*90,'\n')
  return

def consulta_sinopse():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=service,options=options)
    browser.get("https://studioghibli.com.br/filmografia/")

    sleep(2)

    filme = input("Digite o nome do filme: ")
    pesquisa = browser.find_element(by=By.XPATH, value="/html/body//a[contains(text(),'%s')]"%filme)

    sleep(2)

    link = pesquisa.get_attribute("href")
    browser.execute_script("window.open('');") 
    browser.switch_to.window(browser.window_handles[1]) 
    browser.get(link) 

    sleep(2)

    sinopse = browser.find_element(by=By.XPATH, value="//div[@class='wpb_text_column wpb_content_element  luv_dynamic-be63730a']")

    sleep(2)

    print("A sinopse do filme %s é:\n"%filme)
    print(sinopse.text)

    browser.quit

    envia_notion(filme,sinopse.text)

    return

def entrar_conta():
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    browser.get("https://studioghibli.com.br/ghiblistore/minha-conta/")

    sleep(5) 

    input_usuario = input("Digite o seu nome de usuário ou e-mail: ")
    usuario = browser.find_element(by=By.ID, value='username')
    usuario.send_keys('%s'%input_usuario)

    sleep(2)

    input_senha = input("Digite sua senha: ")
    senha = browser.find_element(by=By.ID, value='password')
    senha.send_keys('%s'%input_senha)

    sleep(2)

    input_senha = input("Deseja que o site lembre de seu log-in (s/n)? ")
    if input_senha.upper() == "S":
        botao_lembrar = browser.find_element(by=By.ID, value='rememberme')
        botao_lembrar.click()

    sleep(2)

    botao_login = browser.find_element(by=By.NAME, value='login')
    botao_login.click()

    sleep(5)

    browser.quit
    return

def cadastrar_conta():
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    browser.get("https://studioghibli.com.br/ghiblistore/minha-conta/")

    sleep(5) 

    input_email = input("Digite o seu e-mail: ")
    email = browser.find_element(by=By.ID, value='reg_email')
    email.send_keys('%s'%input_email)

    sleep(2)

    input_nova_senha = input("Digite uma senha: ")
    nova_senha = browser.find_element(by=By.ID, value='reg_password')
    nova_senha.send_keys('%s'%input_nova_senha)

    sleep(2)

    botao_cadastrar = browser.find_element(by=By.NAME, value='register')
    botao_cadastrar.click()

    sleep(2)

    browser.quit
    return

def consulta_nota():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=service,options=options)
    browser.get("https://www.imdb.com/?ref_=nv_home")

    sleep(2) 

    filme = input("Digite o nome do filme: ")
    barra_pesquisa = browser.find_element(by=By.ID, value='suggestion-search')
    barra_pesquisa.send_keys('%s'%filme)
    botao_pesquisar = browser.find_element(by=By.ID, value='suggestion-search-button') 
    botao_pesquisar.click()

    sleep(5)

    link = browser.find_element(by=By.XPATH, value="/html/body//a[contains(text(),'%s')]"%filme)
    link.click()

    sleep(2)

    nota = browser.find_elements(by=By.XPATH, value="/html/body//span[@class='sc-bde20123-1 cMEQkK']")

    sleep(2)
    browser.quit
    print("\nA nota desse filme é %s!\n"%(nota[1].text))

    salvar_dados(filme,nota[1].text)

    return

def envia_notion(nome_filme,sinopse):
  NOTION_TOKEN = "secret_IGUOtVV5pjXian87RpVGHkf40FiGJ4z9FUSYz5tcRQS"
  DATABASE_ID = "90030df9b1604555b20d2aec31bb18b2"

  headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
  }

  create_url = "https://api.notion.com/v1/pages"

  data_adicao = datetime.now().astimezone(timezone.utc).isoformat()

  dados = {
    "Nome": {"title": [{"text": {"content": nome_filme}}]},
    "Sinopse": {"rich_text": [{"text": {"content": sinopse}}]},
    "Data de Adição": {"date": {"start": data_adicao, "end": None}}
  }

  payload = {"parent": {"database_id": DATABASE_ID}, "properties": dados}

  data = json.dumps(payload)

  res = req.post(create_url, headers=headers, data=data)

  if res.status_code == 200:
     print("\nOcorreu tudo certo no envio para o Notion!\n\n")
  else:
     print("\nOcorreu um problema na hora de integrar com o Notion =c\nErro ocorrido: ")
     print(res.status_code)
  return 

def salvar_dados(nome_filme,nota):
  dado = {
    "name":nome_filme,
    "nota":nota
  }
  nome_url = tirar_espaco_string(nome_filme)
  url_crud = "https://crudcrud.com/api/e0d940f4ef8140599928eb29d839ce2c/%s"%nome_url
  response = req.post(url_crud, json=dado)
  if response.status_code == 201:
    print("Dado salvo com sucesso!")
  else:
     print("Ocorreu um erro na hora de salvar o dado! =c")
  return

def tirar_espaco_string(string):
  nova_string = ''
  inicio = 0
  for (i,letra) in enumerate(string):
    if letra == ' ':
      nova_string += string[inicio:i] + '-'
      inicio = i+1
  nova_string+=string[inicio:]
  return nova_string

#Bloco Principal
continuar = True

while continuar:
  menu()

  try:
    opcao = int(input("Digite o número da opção desejada: "))
  except ValueError:
    print("Opção inválida. Digite um número!")
    opcao = False

  if opcao == 1:
     consulta_sinopse()

  elif opcao == 2:
     entrar_conta()

  elif opcao == 3:
     cadastrar_conta()

  elif opcao == 4:
     consulta_nota()

  elif opcao == 5:
    continuar = False

  elif opcao:
    print("Número inválido. Digite um dos números listados!")

