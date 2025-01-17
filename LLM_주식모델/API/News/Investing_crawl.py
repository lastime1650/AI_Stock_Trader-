from typing import Optional, List, Dict

import requests
from bs4 import BeautifulSoup

from LLM_주식모델.crawl.crawl_module import Crawl

class Inversting_crawl():
    def __init__(self):
        pass

    # 통화 뉴스
    def Get_Currency_news(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/forex-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 평가
    def Get_Analyst_Ratings(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/analyst-ratings"
        return self._get_News_list(url, url)

    # 주식 상품 뉴스
    def Get_Commodities_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/commodities-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 일반 주식 뉴스
    def Get_Stock_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/stock-market-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 경제 지표 뉴스
    def Get_Economy_indicator_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/economic-indicators"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 경제 뉴스
    def Get_Economy_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/economy"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 암호화폐 뉴스
    def Get_Cryptocurrency_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/cryptocurrency-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 내부 트레이딩(내부자 거래) 뉴스
    def Get_Trading_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/insider-trading-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 회사 뉴스
    def Get_Company_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/company-news"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 수입 뉴스
    def Get_Earnings_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/earnings"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 투자 아이디어 뉴스
    def Get_Investment_Ideas_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/investment-ideas"
        return self._get_news_by_a_page(url, url, maximum_page)

    # SWOT 뉴스
    def Get_SWOT_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/swot-analysis"
        return self._get_news_by_a_page(url, url, maximum_page)

    # 실적 발표 뉴스
    def Get_Transcripts_News(self, maximum_page:int=2) -> Optional[List[Dict]]:
        url = "https://www.investing.com/news/transcripts"
        return self._get_news_by_a_page(url, url, maximum_page)




    # 최신 뉴스 ( 이 친구는 Page 1개 밖에 안됨 )
    def Get_Latest_News(self,none:str="") -> Optional[List[Dict]]:
        print("뉴스호출됨")
        url = "https://www.investing.com/news/latest-news"
        return self._get_News_list(url, "https://www.investing.com/news")



    ####################################################################################################################
    # 내부 메서드

    # [1/3] Page 단위 뉴스 목록기반 가져오기
    # 이는 ._get_News_list() 메서드를 여러번 호출하는 형태로 상위 로직임
    def _get_news_by_a_page(self, url:str, sub_dir_name_for_startswith:str, maximum_page:int=1) -> Optional[List[Dict]]:
        Output = []
        for i in range(0, maximum_page):

            #url = f"https://www.investing.com/news/forex-news/{i + 1}"
            url_ = f"{url}/{i+1}"
            articles = self._get_News_list(url_, sub_dir_name_for_startswith)#"https://www.investing.com/news/forex-news")
            if not articles:
                break
            else:
                Output.extend(articles)
        return Output

    # [2/3] 뉴스 목록 가져오기
    def _get_News_list(self, url: str, sub_dir_name_for_startswith:str) -> Optional[List[Dict]]:
        '''
            1. "주식 뉴스 목록 가져오기"
            2. (1) 목록 당 url 접근 후 articl 내용 가져오기 ( ._extract_article() 에서 진행된다.  )
        '''
        latest_news_list: List[str] = []

        # url = "https://www.investing.com/news/analyst-ratings"
        latest_news_list_soup = Crawl(url)
        # 1-1 시그니처 -> <ul data-test="news-list"> 로 접근한다.
        news_list = latest_news_list_soup.find("ul", attrs={"data-test": "news-list"})  # .find() 하위 태그까지 모두 찾아줌

        # 1-2 <a> 태그인 것만을 찾으며, href 속성을 가져온다
        for link in news_list.find_all("a"):
            idk_link = link.get('href')
            #print(idk_link)
            # 정확한 뉴스만 필터링
            if (idk_link.startswith(sub_dir_name_for_startswith)  # "https://www.investing.com/news/analyst-ratings")  # 앞 부분 시그니처
                    and
                    (not idk_link.endswith("#comments"))  # 쓰잘데기 없는거 제외
            ):
                # print(f"Link: {idk_link}")
                latest_news_list.append(idk_link) # 여기가 하나씩 기사 url가 추가됨

        #print(latest_news_list)
        articles = self._extract_article(latest_news_list)  #

        return articles


    # [3/3]
    # 1개 이상의 기사 URL ->
    # -> 기사 내용 가져옴
    def _extract_article(self, article_urls:List[str])->Optional[List[Dict]]:
        Output:List[Dict] = []
        for url in article_urls:
            tmp = {}
            # 2-1 목록 당 url 접근 후 articl 내용 가져오기
            print(url)
            latest_news_list_soup = Crawl(url)

            # 2-2 제목
            title = latest_news_list_soup.find("title").text

            # 2-3 기사 타임스탬프
            article_timestamp = ""
            # 시그니처 -> <div class="flex flex-col gap-2 text-warren-gray-700 md:flex-row md:items-center md:gap-0">
            # select_one이면 한방에 찾음

            article_spans = latest_news_list_soup.select_one("div.flex.flex-col.gap-2.text-warren-gray-700.md\\:flex-row.md\\:items-center.md\\:gap-0") # ":"앞에는 \\ 을 넣어야 구분자 취급
            if not article_spans:
                print(url)
            article_spans_list = list( article_spans.select("span") )
            article_timestamp = article_spans_list[0].text
            #print(article_timestamp)

            # 2-4 기사 내용 추출 (여러 <p> 태그이므로 반복추가)
            content = ""
            target_divs = latest_news_list_soup.find_all("div", class_="article_container", id="article")
            for div in target_divs:
                #print(f"find_all() 사용: {div}")
                #print( div.select("p"))
                for article_sentence in div.select("p"):
                    #print(article_sentence.text)
                    content += article_sentence.text

            tmp["title"] = title
            tmp["Published_Timestamp"]= article_timestamp
            tmp["article_content"] = content.split("This article was generated with the support of AI and reviewed by an editor.")[0]
            Output.append(tmp)
        return Output

    ## 아래는 잘 안쓰는 것들 ##

    # 분석 글 (주관적)
    def Get_Analysis_News(self):
        analysis_list: List[str] = []

        url = "https://www.investing.com/analysis/etfs"
        latest_news_list_soup = Crawl(url)
        # 1-1 시그니처 -> <div id="contentSection" class="float_lang_base_2 articlesFilter mediumTitle1 analysisImg"> 로 접근한다.

        news_list = latest_news_list_soup.find("div", class_="float_lang_base_2 articlesFilter mediumTitle1 analysisImg")  # .find() 하위 태그까지 모두 찾아줌
        #print(news_list)
        for link in news_list.find_all("a"):
            try:
                if link.get('class')[0] == "title":
                    get_article_url = link.get('href')
                    if get_article_url:
                        if get_article_url.startswith("/analysis/"):
                            complete_url = f"https://www.investing.com{get_article_url}"
                            #print(complete_url)
                            analysis_list.append(complete_url)


            except:
                continue
        return self._extract_article(analysis_list)

    # 인기가 많은 분석 글 ( 대용량이라 나눠서 해야함 )
    def Get_Popular_Analysis_News(self):
        analysis_list: List[str] = []

        url = "https://www.investing.com/analysis/most-popular-analysis"
        latest_news_list_soup = Crawl(url)
        # 1-1 시그니처 -> <div class="largeTitle analysisImg"> 로 접근한다.
        news_list = latest_news_list_soup.find("div", class_="largeTitle analysisImg")  # .find() 하위 태그까지 모두 찾아줌
        for link in news_list.find_all("a"):
            try:
                if link.get('class')[0] == "title":
                    get_article_url = link.get('href')
                    if get_article_url:
                        if get_article_url.startswith("/analysis/"):
                            complete_url = f"https://www.investing.com{get_article_url}"
                            # print(complete_url)
                            analysis_list.append(complete_url)


            except:
                continue

        return self._extract_article(analysis_list)


#print( Inversting_crawl().Get_Latest_News() )