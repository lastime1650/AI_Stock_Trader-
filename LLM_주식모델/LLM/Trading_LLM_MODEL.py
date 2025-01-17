import asyncio
import queue
import threading
from logging import PlaceHolder
from typing import Optional, List, Any, Dict, Union
import requests
import json
from langchain.chains.question_answering.map_rerank_prompt import output_parser
from langchain.llms.ollama import Ollama # ollama LLM모델
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.utils import Input

# 에이전트 관련
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, create_react_agent, AgentExecutor, AgentType, \
    ConversationalAgent  # 함수 호출
from langchain.agents.agent import AgentOutputParser

# 뉴스 추출 모듈
from LLM_주식모델.API.News.Investing_crawl import Inversting_crawl

# 주식 정보 추출 모듈
from LLM_주식모델.API.Invest.Yahoo.Yahoo_Finance import Yahoo_Finance

class Trading_LLM():
    def __init__(self, model:Any, Conversation_ID:str):

        # 함수를 위한 인스턴스
        self.NEWS = Inversting_crawl()
        self.INVEST = Yahoo_Finance()

        # LLM 기본 정보
        self.model = model

        self.Build_Agent_LLM(Conversation_ID)

    def Build_Agent_LLM(self,Conversation_ID:str):

        # 대화 메모리 버퍼 생성
        ConversationMemoryBuffer = ConversationBufferMemory(memory_key=Conversation_ID, return_messages=True)

        # 프롬프트 생성
        Prompt = self._Set_Prompt(Conversation_ID)

        # TOol 생성
        Tools = self._Set_Tools()

        # 에이전트  생성
        react_agent = create_react_agent(
            llm=self.model,
            tools=Tools,
            prompt=Prompt
        )

        # 모델 Executor 생성
        self.executor = AgentExecutor.from_agent_and_tools(
            agent=react_agent,
            tools=Tools,
            memory=ConversationMemoryBuffer,
            verbose=True,
            handle_parsing_errors=True
        )

    def _Set_Prompt(self, ConversationID: str) -> PromptTemplate:

        main_prompt = '''You are an experienced stock trader and financial expert. Your mission is to carefully analyze the latest stock-related articles, summarize the core clearly, and provide wise investment directions based on them. You have the ability to communicate complex financial information clearly and concisely so that even the general public can understand it easily.
        
        **Key missions:**
        
        1. **Summary of the article:**
        - Read the provided article closely and summarize the core content concisely and clearly.
        - It should include the main points of the article, the companies/industries involved, market trends, positive/negative factors, etc.
        - Technical terms should be explained in a way that the general public can understand.
        
        2. **Investment Analysis:**
        - Based on the article, analyze the investment opportunities and risks for the company/industry.
        - Explain specifically the impact of positive/negative factors on stock prices.
        - Provide investment prospects from a short-term and long-term perspective.
        - Evaluate relative investment attractiveness through comparative analysis with similar industries/companies.
        
        3. **Presenting investment direction:**
        - Based on the results of investment analysis, specific investment strategies (buy, sell, hold, etc.) are presented.
        - Provide a clear basis and logic for the investment strategy presented.
        - We provide investment guidelines by presenting specific figures such as target stock prices and loss prices.
        - We propose a variety of investment portfolio composition plans according to investors' risk-taking tendencies.
        
        4. **Write a report:**
        - Combine the above to create a systematic and readable report.
        - The report consists of a clear title, outline, body (article summary, investment analysis, investment direction), and conclusion.
        - If necessary, use charts, graphs, tables, etc. to deliver information visually.
        - The report should be written in a professional and easy-to-understand style.
        
        **Precautions:**
        
        - All analyses and suggestions should be based on the articles and objective data provided.
        - Personal opinions or biased interpretations should be excluded.
        - It should be stated that investment always carries risks and that this report should only be used as a reference for investment decisions.
        - You must adhere to ethical standards and be responsible.\n'''

        PREFIX = """당신은 이전 대화를 기억하고 필요할 때 도구를 사용할 수 있는 주식 트레이더입니다.

        당신은 다음 도구들을 사용할 수 있습니다: {tools}
        
        이전 대화:
        {""" + ConversationID + """}
        
        관련이 있을 때는 항상 채팅 기록을 기반으로 사용자의 질문에 답변하십시오. 계산을 수행해야 하는 경우 적절한 도구를 사용하십시오."""

        FORMAT_INSTRUCTIONS = """\n다음 형식을 사용하십시오:
        Question: 당신이 답해야 할 입력 질문
        Thought: 당신이 무엇을 해야 할지 항상 생각해야 합니다
        Action: 취해야 할 행동, [{tool_names}] 중 하나여야 하며, 도구가 필요하지 않은 경우 직접 응답합니다
        Action Input: 도구를 사용하는 경우 해당 도구에 대한 입력
        Observation: 도구를 사용한 경우 그 결과
        ... (이 Thought/Action/Action Input/Observation은 N번 반복될 수 있습니다)
        Thought: 이제 최종 답변을 알겠습니다
        Final Answer: 원래 입력 질문에 대한 최종 답변, 꼭 마무리할 때는 `Final Answer:`에 응답을 넣고해야 정상 종료됩니다.\n"""

        SUFFIX = """시작!

        Question: {input}
        Thought:{agent_scratchpad}"""

        #프롬프트 구성
        prompt_template = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", ConversationID],
            template= PREFIX + FORMAT_INSTRUCTIONS + SUFFIX
        )


        return prompt_template

    def _Set_Tools(self)->List[Tool]:
        Tools = []
        Tools.append(
            Tool(
                name="Scan stock information",
                func=self.INVEST.Get_time_series,
                description="""
                        **함수 설명:**
                        
                        이 함수를 사용하기 전에 최종 뉴스를 확인하여 현 상황을 파악하세요
                        
                        사용자가 입력한 주식 종목(Symbol)에 대한 시계열 데이터와 관련 정보를 분석하여, 현재 주식 동향을 파악하고 미래 전망을 예측하는 역할을 수행합니다.
                        *만약 사용자가 입력한 말에 주식 종목이 포함되어 있지 않으면 다시 입력을 요구하라고 Final Answer 하세요
                        
                        **요청 사항:**
                        
                        주어진 주식 Symbol에 대한 최신 시계열 데이터와 관련 정보를 수집하여 분석하고, 이를 바탕으로 사용자에게 명확하고 유용한 정보를 제공해야 합니다. 분석에는 기술적 지표, 시장 심리, 관련 뉴스 등 다양한 요소를 종합적으로 고려해야 합니다. 
                        
                        **인자 설명:**
                        
                        - **`symbol` (필수):**
                            - **타입:** `string`
                            - **설명:** 사용자가 분석을 원하는 주식 종목의 Symbol (예: AAPL, TSLA, 005930.KS)
                            - **형식:**  JSON 형식으로 제공
                            
                        - **`period` (필수):**

                            타입: string
                            설명: 시계열 데이터의 기간 범위를 지정합니다. 아래 값 중 하나를 선택해야 합니다
                            가능한 값: 1d, 5d
                            1d: 1일
                            5d: 5일 (현재 프롬프트에서 최대로 허용하는 값)
                            제한: 현재 설정에서 최대 허용값은 5d (5일)입니다.
                            형식: JSON 형식으로 제공
                            
                        - **`interval` (필수):**
                            타입: string
                            설명: 시계열 데이터의 시간 간격을 지정합니다. 아래 값 중 하나를 선택해야 합니다.
                            가능한 값: 5m, 15m, 30m, 60m, 90m, 1h
                            5m: 5분 
                            15m: 15분
                            30m: 30분
                            60m: 60분
                            90m: 90분
                            1h: 1시간
                            제한: 최소 허용값은 5m (5분)입니다. 
                            
                            형식: JSON 형식으로 제공
                            예시:
                            ```json
                            {
                              "symbol": "AAPL",
                              "period": "1d",
                              "interval": "5m"
                            }
                            ```
                        
                        **응답 형식:**
                        
                        - **`report` (필수):**
                            - **타입:** `object`
                            - **설명:** 주식 분석 보고서. 아래 항목들을 포함해야 합니다.
                                - **`summary` (필수):**
                                    - **타입:** `string`
                                    - **설명:** 주식 현재 상황에 대한 간결하고 명확한 요약. 시계열 데이터 분석 결과와 주요 특징을 포함해야 합니다. 예를 들어, "최근 6개월간 상승 추세, 주요 저항선 돌파 시도 중"과 같이 작성합니다.
                                - **`technical_analysis` (필수):**
                                    - **타입:** `object`
                                    - **설명:** 기술적 분석 결과.
                                        - **`trend` (필수):**
                                            - **타입:** `string`
                                            - **설명:** 현재 주가 추세 (예: 상승, 하락, 횡보)
                                        - **`support_levels` (필수):**
                                            - **타입:** `array`
                                            - **설명:** 주요 지지선 가격들
                                        - **`resistance_levels` (필수):**
                                            - **타입:** `array`
                                            - **설명:** 주요 저항선 가격들
                                        - **`indicators` (선택):**
                                            - **타입:** `object`
                                            - **설명:** 사용된 기술적 지표와 그 해석 (예: 이동평균선, RSI, MACD)
                                - **`news_sentiment` (선택):**
                                    - **타입:** `string`
                                    - **설명:** 관련 최신 뉴스의 전반적인 분위기 (예: 긍정적, 부정적, 중립적)
                                - **`future_outlook` (필수):**
                                    - **타입:** `string`
                                    - **설명:**  종합적인 분석을 바탕으로 한 미래 주가 전망. 객관적 근거를 기반으로 작성해야 하며, "예측이 어려울 경우, 그 이유와 함께 추가 정보의 필요성"을 명시해야 합니다. 불확실성을 인정하고 무리한 예측을 지양해야 합니다.
                                - **`recommendation` (선택):**
                                    - **타입:** `string`
                                    - **설명:** 투자 관련 제안 (예: 매수, 매도, 보유), 단, 신중하게 제시해야 하며, "투자에 대한 책임은 투자자 본인에게 있음"을 명시해야 합니다.
                                - **`additional_info` (선택):**
                                    - **타입:** `string`
                                    - **설명:**  분석에 참고한 주요 정보 출처, 또는 추가적으로 고려해야 할 사항 등
                                    
                        [1급 중요사항]-그리고 꼭 최종 응답할 때, `Final Answer:`이후에 분석 결과를 작성해야만 정상 종료됩니다. 
                        
                        **성공적인 응답을 위한 지침:**
                        
                        1. **객관성 유지:**  모든 분석은 객관적인 데이터와 근거를 기반으로 해야 합니다. 개인적인 의견이나 편향된 해석은 배제해야 합니다.
                        2. **정확성 확보:**  정확한 최신 데이터를 사용해야 하며, 데이터 출처를 명확히 해야 합니다.
                        3. **명확한 표현:**  전문 용어 사용을 최소화하고, 일반 사용자도 이해할 수 있도록 명확하고 간결하게 작성해야 합니다.
                        4. **불확실성 인정:**  주식 시장은 본질적으로 불확실성을 내포하고 있음을 인지하고, 무리한 예측을 지양해야 합니다.
                        5. **윤리적 책임:**  투자 조언은 신중하게 제공해야 하며, 모든 투자의 책임은 투자자 본인에게 있음을 명확히 밝혀야 합니다.
                        
                        **지켜야할 사용자를 위한 응답 형식**  
                            만약 사용자에게 최종 응답을 하려는 경우, 문장 맨 앞에 `Final Answer:`을 기입하고 결과 설명을 기입합니다. 그리고 다음과 같은 JSON형식으로 반환하세요
                        
                        Final Answer:<<총 결론 요약>>```json
                        {
                          "report": {
                            "summary": "최근 1년간 박스권 횡보, 최근 거래량 증가하며 상승 돌파 시도",
                            "technical_analysis": {
                              "trend": "횡보 후 상승 시도",
                              "support_levels": [
                                150,
                                145
                              ],
                              "resistance_levels": [
                                160,
                                165
                              ],
                              "buy_price": 추천 매숫값,
                              "sell_price": 추천 매도값,
                              "indicators": {
                                "MA20": "상승 추세",
                                "RSI": "과매수 구간 진입"
                              }
                            },
                            "news_sentiment": "긍정적",
                            "future_outlook": "신제품 출시에 대한 기대감으로 단기 상승 가능성. 다만, 경쟁 심화에 대한 우려 존재. 장기 전망은 불확실.",
                          }
                        }
                        """
                )
            )

        Tools.append(
            Tool(
                name="Read the latest stock news",
                func=self.NEWS.Get_Latest_News,
                description="""
                        **함수 설명:**
                            최신화된 주식 뉴스를 검색할 수 있으며 주식 동향과 가능성을 검토하는데에 도움이 됩니다. 
                            자주 사용하지 마세요 성능 저하가 발생됩니다. 
                        **인자 정보:**
                            따로 인자는 필요하지 않습니다.
                        **반환 정보:**
                            리스트안에 여러 json이 저장된 형태로, 2개이상의 기사가 반환됩니다.
                        **지켜야할 사용자를 위한 응답 형식**
                            만약 사용자에게 최종 응답을 하려는 경우, 문장 맨 앞에 `Final Answer:`을 기입하고 다음과 같은 JSON형식으로 반환하세요
                            Final Answer:```json
                            {
                                "summary": "여러 뉴스를 요약하고 추세를 응답"
                                "article_results": [] //투자에 영향이 끼칠 기사 및 알아서 기사에 대한 요약을 동적으로 집어넣으세요 "str"타입 
                            }
                            ```
                            """
                        )
        )
                        
                        


        return Tools

    def Query(self, query:str):
        return self.executor.invoke(
            {
                "input":query
            }
        )


inst = Trading_LLM(
ChatOpenAI(  # LLM 자원 ( default )
                        model="gpt-4o-mini",  # 모델을 지정 (gpt-4o-mini)
                        temperature=0.7,  # 응답 다양성 조정
                        openai_api_key="API KEY HERE!!@@#$@#$@#%#$%#$%#$%#$%#$%#$%#$%"
                        # OpenAI API 키 설정
                    ),
    "TEST"
)

#r = inst.Query("당신은 누구입니까?")

#print(r)

#
while True:
    print(inst.Query(input())  )

'''r = inst.Query("현재 뉴스좀 보고해")
print(r)

r = inst.Query("자 그러면 이제 애플의 AAPL 종목을 한번 봐줘")
print(r)

r = inst.Query("아까 뉴스 결과랄 합해서 보았을 때 연관성은 무엇이 있을까? 1문장으로 간단히 응답해")
print(r)'''