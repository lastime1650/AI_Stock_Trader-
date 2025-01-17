import requests
from bs4 import BeautifulSoup

def Crawl(url:str)->BeautifulSoup:
    response = requests.get(url)
    response.encoding = 'utf-8' # 인코딩 설정
    soup = BeautifulSoup(response.text, "html.parser")
    return soup