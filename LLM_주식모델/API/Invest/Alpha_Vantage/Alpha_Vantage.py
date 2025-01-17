from enum import Enum
from typing import Optional
import yfinance

class AlphaVantage_interval(Enum):
    onemin = "1min"
    fivemin = "5min"
    fifteenmin = "15min"
    thirtymin = "30min"
    hour = "60min"

import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
#url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=TQQQ&interval=1min&apikey=9M2PTFJLG7VBE4Z9'
#url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=9M2PTFJLG7VBE4Z9"
#r = requests.get(url).json()
#print(r)

#print(f"{data}".replace("'",'"'))

class AlphaVantage_API:
    def __init__(self, api_key:str):
        self.api_key = api_key
        self.url = f"https://www.alphavantage.co/query"

    def Get_Data(
            self,
            # 필수
            symbol:str, # 주식 명
            interval:AlphaVantage_interval, # 시간 간격
            function: str="TIME_SERIES_INTRADAY",  # 시계열 함수

            # 선택
            outputsize:str="compact", # 출력 크기
            extended_hours:Optional[str]=None,
            month:Optional[str]=None, # (YYYY-MM) 형식

    )->dict:
        '''
        {
            "Meta Data": {} 별로 안중요함
            "Time Series": [{},{},,] 중요 시계열 데이터 (차트 읽는게 가능하다 )
        }
        '''
        default_url = f"{self.url}?function={function}&symbol={symbol}&interval={interval.value}&apikey={self.api_key}"
        if outputsize:
            default_url += f"&outputsize={outputsize}"
        if extended_hours:
            default_url += f"&extended_hours={extended_hours}"
        if month:
            default_url += f"&month={month}"

        r = requests.get(default_url)
        data = r.json()

        return data


    def Get_News(
            self,
            symbol:str, # 주식 명 (ETF말고)
            function:str="NEWS_SENTIMENT",  # 시계열 함수
    )->dict:
        '''
        {
            'items': 정수
            'sentiment_score_definition': 문자열
            'relevance_score_definition': 문자열
            'feed' : [] -> 중요! 관련 뉴스 리스트임
        }
        '''
        default_url = f"{self.url}?function={function}&tickers={symbol}&apikey={self.api_key}"
        r = requests.get(default_url).json()

        return r

    # Get_News에서 얻은 URL에 대한 스크랩
    def Url_to_Data(self, url:str)->str:
        return requests.get(url).text

inst = AlphaVantage_API("9M2PTFJLG7VBE4Z9")
#print( f'{AlphaVantage_API("9M2PTFJLG7VBE4Z9").Get_Data(symbol="TQQQ", interval=AlphaVantage_interval["onemin"])}')

print( f'{inst.Get_News(symbol="AAPL")}')