
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


class Search_Web():

    def search_web(self,search_term,search_engine):
        match search_engine:
            case "serpapi":
                SERP_API_KEY = os.environ.get('SERP_API_KEY')
                url = f"https://serpapi.com/search.json?q={search_term}&api_key={SERP_API_KEY}"
                response = requests.get(url)
                data = response.json()
                #print(data)
                return data
            
            case "serper":
                SERPER_DEV_KEY=os.environ.get('SERPER_DEV_KEY')
                url = "https://google.serper.dev/search"
                payload = json.dumps({
                    "q": search_term
                })
                headers = {
                'X-API-KEY': SERPER_DEV_KEY,
                'Content-Type': 'application/json'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                data=response.json()
                #print(data)
                return data
            
            case "search1api":
                key=os.environ.get('SEARCH_API_KEY')
                SEARCH_API_KEY="Bearer "+str(key)

                url = "https://api.search1api.com/search"

                payload = {
                    "query": search_term,
                    "search_service": "google",
                    "max_results": 5,
                    "crawl_results": 2,
                    "image": True,
                    #"gl": "<string>",
                    #"hl": "<string>"
                }
                headers = {
                    "Authorization": SEARCH_API_KEY,
                    "Content-Type": "application/json"
                }
                #print(SEARCH_API_KEY)
                response = requests.request("POST", url, json=payload, headers=headers)

                data=response.json()
                #print(data)
                return data
            
            case "searchapi":
                SEARCHAPI_SEARCH_ENDPOINT = "https://www.searchapi.io/api/v1/search"
                #"""
                #Search with SearchApi.io and return the contexts.
                #"""
                REFERENCE_COUNT = 8
                subscription_key = os.environ.get("SEARCHAPI_KEY")
                payload = {
                    "q": search_term,
                    "engine": "google",
                    "num": (
                        REFERENCE_COUNT
                        if REFERENCE_COUNT % 10 == 0
                        else (REFERENCE_COUNT // 10 + 1) * 10
                    ),
                }
                headers = {"Authorization": f"Bearer {subscription_key}", "Content-Type": "application/json"}
                
                response = requests.get(
                    SEARCHAPI_SEARCH_ENDPOINT,
                    headers=headers,
                    params=payload,
                    timeout=30,
                )
                if not response.ok:
                    print(response.status_code, "Search engine error.")
                data = response.json()
                #print(data)
                return data
            
            case "bing":
                DEFAULT_SEARCH_ENGINE_TIMEOUT = 5
                BING_MKT=os.environ.get('BING_MKT')
                BING_SEARCH_V7_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
                params = {"q": search_term, "mkt": BING_MKT}
                response = requests.get(
                    BING_SEARCH_V7_ENDPOINT,
                    headers={"Ocp-Apim-Subscription-Key": subscription_key},
                    params=params,
                    timeout=DEFAULT_SEARCH_ENGINE_TIMEOUT,
                )
                if not response.ok:
                    print(response.status_code, "Search engine error.")
                data = response.json()
                #print(data)
                return data
            
            case "google":
                subscription_key=os.environ.get['GOOGLE_SEARCH_API_KEY']
                cx=os.environ.get('GOOGLE_SEARCH_CX')
                REFERENCE_COUNT = 8
                GOOGLE_SEARCH_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
                params = {
                    "key": subscription_key,
                    "cx": cx,
                    "q": search_term,
                    "num": REFERENCE_COUNT,
                }
                response = requests.get(
                    GOOGLE_SEARCH_ENDPOINT, params=params, timeout=DEFAULT_SEARCH_ENGINE_TIMEOUT
                )
                if not response.ok:
                    print(response.status_code, "Search engine error.")
                data = response.json()
                #print(data)
                return data
