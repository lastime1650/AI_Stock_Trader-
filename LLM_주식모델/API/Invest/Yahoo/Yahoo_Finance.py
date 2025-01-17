from typing import Optional, List

import yfinance as yf
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
'''
# 종목 티커 지정
ticker = "TQQQ"

# 종목에 대한 데이터 가져오기 (예: 최근 1개월간의 일일 종가 데이터)
stock = yf.Ticker(ticker)

# 시계열 데이터 가져오기 (예: '1d' 단위, 1개월)
#output = stock.history(period="1mo", interval="1d")
output = stock.history(period="1d", interval="1m")
DF = pd.DataFrame(output)
print(DF.columns)

for data in DF.itertuples():
    print(data)

   #data[0] -> 타임스탬프 추출
    #data[1] -> 주식 데이터 추출

print(dict(stock.info)) # 회사 정보 - json
print(stock.financials) # 연간 재무제표 - DataFrame / ETF의 경우는 데이터 없음
print(stock.quarterly_financials)# 분기별 재무제표 - DataFrame / ETF의 경우는 데이터 없음
print(stock.balance_sheet) # 재고표 - DataFrame
print(stock.cashflow) # 연간/분기별 현금흐름표
#print(stock.earnings) # 연간/분기별 순이익표(EPS) - 유료
print(stock.recommendations) # 애널리스트의 매수/매도/보유 의견 목표 주가 제공
print(stock.calendar) # 일정

print(stock.earnings_history) # 연간 순이익 내역
print(stock.dividends) # 이자 내역
print(stock.splits) # 주식 분할 내역

'''
import json
#print(historical_data)

#print(stock.balance_sheet)

class Yahoo_Finance:
    def __init__(self):
        pass

    # 시계열 데이터 가져오기 (예: '1d' 단위, 1개월)
    def Get_time_series(
            self,
            test:str
            #stock_name:str,
            #period:str, # period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            #interval:str # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    )->Optional[dict]:

        test = test.replace("```json","").replace("```","").replace(" ","").replace("\n","")
        test = test.split("}")[0] + "}"
        test = f'{{{test.split("{")[1]}'
        print(test)
        test= json.loads(test)
        stock_name = test["symbol"]
        period = test["period"]
        interval = test["interval"]
        '''
         올인원으로 처리하자
        '''
        stock = None
        try:
            stock = yf.Ticker(stock_name)
        except:
            # 주식 이름이 없을 경우
            return None

        OUTPUT = {}  # 최종 반환

        '''
            시계열 데이터 가져오기
        '''
        OUTPUT["time_series"] = []
        DF = stock.history(period=period, interval=interval)

        time_series_keys_by_this_columns = list( DF.columns ) # ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        for data in DF.itertuples():
            tmp = {}

            # 타임스탬프
            info = data[0]
            tmp["Timestamp"] = info

            # 시계열 데이터 구축
            time_series = data[1:]
            for i, key in enumerate(time_series_keys_by_this_columns):
                tmp[key] = time_series[i]

            #print(info)
            #print(time_series)
            #print(tmp)

            OUTPUT["time_series"].append(tmp)
        print(OUTPUT["time_series"])

        '''
            기업 정보 수집하기
        '''
        # 1. 기업 정보
        OUTPUT.update(dict(stock.info)) # 이어붙이기


        print(OUTPUT)
        return OUTPUT

    #
'''
inst = Yahoo_Finance()
inst.Get_time_series(
    stock_name="AAPL",
    period="1d",
    interval="1m"
)'''