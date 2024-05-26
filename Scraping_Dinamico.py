from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tqdm import tqdm
import time

def setup_driver():
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get('https://lmmobilidade.com.br/lmseminovos/veiculos/?search_car=&order=&amout_year=2016%20-%202023&amout=R%24%2044900%20-%20R%24%20535900&select_cambio=')
    return driver

def click_load_more(driver):
    try:
        # Configura um contador para salvar a cada 10 cliques
        count = 0
        while True:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".button-load-more .button[data-button='current']"))
            )
            button.click()
            count += 1
            time.sleep(2)  # Ajuste este tempo conforme necessário
            if count % 10 == 0:
                data = extract_data(driver)
                save_data_to_excel(data)
    except Exception as e:
        print("Todos os modelos foram carregados ou ocorreu um erro:", str(e))

def extract_data(driver):
    data = []
    veiculos = driver.find_elements(By.CSS_SELECTOR, "a.item.highlight, a.item")
    for veiculo in veiculos:
        url = veiculo.get_attribute('href') if veiculo else "URL não especificada"
        imagem_elements = veiculo.find_elements(By.CSS_SELECTOR, "div.image img")
        imagem_url = imagem_elements[0].get_attribute('src') if imagem_elements else "Sem imagem"

        marca = veiculo.find_element(By.CSS_SELECTOR, "div.brand span").text if veiculo.find_elements(By.CSS_SELECTOR, "div.brand span") else "Marca não especificada"
        modelo = veiculo.find_element(By.CSS_SELECTOR, "div.name span").text if veiculo.find_elements(By.CSS_SELECTOR, "div.name span") else "Modelo não especificado"
        versao = veiculo.find_element(By.CSS_SELECTOR, "div.version span").text if veiculo.find_elements(By.CSS_SELECTOR, "div.version span") else "Versão não especificada"

        info_div_elements = veiculo.find_elements(By.CSS_SELECTOR, "div.info")
        if info_div_elements:
            info_div = info_div_elements[0]
            small_elements = info_div.find_elements(By.CSS_SELECTOR, "small")
            quilometragem = small_elements[0].text if len(small_elements) > 0 else "Quilometragem não especificada"
            combustivel = small_elements[1].text if len(small_elements) > 1 else "Combustível não especificado"
            ano = small_elements[2].text if len(small_elements) > 2 else "Ano não especificado"
        else:
            quilometragem = combustivel = ano = "Informação não disponível"

        valor = veiculo.find_element(By.CSS_SELECTOR, "div.price span").text.strip() if veiculo.find_elements(By.CSS_SELECTOR, "div.price span") else "Valor não especificado"
        localizacao = veiculo.find_element(By.CSS_SELECTOR, "div.location span").text if veiculo.find_elements(By.CSS_SELECTOR, "div.location span") else "Localização não especificada"

        # Assegura que a ordem dos dados está correta
        data.append([marca, modelo, versao, quilometragem, ano, combustivel, valor, localizacao, url, imagem_url])
    return data


def save_data_to_excel(data, filename="veiculos.xlsx"):
    df = pd.DataFrame(data, columns=["Marca", "Modelo", "Versão", "Quilometragem", "Ano", "Combustível", "Valor", "Localização", "URL", "Imagem URL"])
    df.to_excel(filename, index=False)
    print(f"Dados salvos em {filename} até o momento.")


driver = setup_driver()
click_load_more(driver)
driver.quit()  # Encerra o navegador
