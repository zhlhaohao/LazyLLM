import asyncio
import lazyllm
from lazyllm import fc_register, ReWOOAgent, deploy, pipeline, bind
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import aiohttp
import os
from lazyllm import LOG
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, RoundRobinProxyStrategy, ProxyConfig
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from lazyllm.tools.agent import ReactAgent
from .utils import extract_relevant_context
from datetime import datetime

search_max_results = 2


PROMPT_TEMPLATE = """
你是一位网络爬虫，需要基于用户给定的问题从网络上收集信息。你的工作流程如下：

1. 将用户问题调用搜索工具从网络得到url list。
2. 对url list调用爬虫工具进行网页爬取，获取详细的资料

3. 错误处理
   - 如果出现错误则退出。

你需要给出所引用的参考资料的page url
   
Query：
{query}
"""

# @fc_register("tool")
# def get_current_date_us_full():
#     """
#     Returns the current date in full US format (Month DD, YYYY)
    
#     Returns:
#         str: Current date in Month DD, YYYY format, like "July 04, 2025"
#     """
#     today = datetime.now()
#     return today.strftime("%B %d, %Y")


@fc_register("tool")
def WebSearchTool(query: str, language: str = "zh-CN", time_range: str = ""):
    """Worker that search web pages using searxng, input should be a query.

    Args:
        query (str): user query.    
        language (str, optional): language of the query". 
        time_range (str): [year|month|week|day], time range of the search. time_range=year when query contains "this year", time_range=month when query contains "this month", time_range=week when query contains "this week", time_range=day when query contains "today". 
    """
    return asyncio.run(searxng_search(query, language, time_range))


@fc_register("tool")
def CrawlPagesTool(page_url_list: List[str], query: str):
    """
    Worker that crawl web page contents. Input should be a list of page url.

    Args:
        page_url_list (List[str]): list of page url to crawl.
        query (str): user query.

    """
    return asyncio.run(crawl_many_pages(page_url_list, query))


async def crawl_many_pages(page_url_list: List[str], query: str):
    # crawl4ai爬取url的内容，询问大模型词网页是否有用，有用则返回与用户提问相关的片段
    # 创建信号量限制并发数为3,一个批次启动3个任务

    try:
        semaphore = asyncio.Semaphore(5)

        async def process_link_with_sem(link):
            async with semaphore:
                return await crawl_single_page(link, query)

        # 每个批次的任务间隔1秒启动
        async def delayed_task(index, link):
            await asyncio.sleep(index * 1)
            return await process_link_with_sem(link)

        # 创建所有任务批次,开始执行,120不能太短了，因为除了爬虫还有一个提取摘要的过程要花时间
        tasks = [
            asyncio.wait_for(delayed_task(i, link), timeout=120)
            for i, link in enumerate(page_url_list)
        ]
        # 收集结果
        link_results = await asyncio.gather(*tasks, return_exceptions=True)
        link_results = [
            res for res in link_results if not isinstance(res, Exception)
        ]

        # 去掉None值
        iteration_contexts = []
        i = 0
        for res in link_results:
            if res:
                iteration_contexts.append(res)
                i += 1

        content =  "\n\n".join(iteration_contexts)
        return content
    except Exception as e:
        LOG.error(f"Crawl Pages error: {e}")
        return str(e)

async def crawl_single_page(page_url: str, query: str):
    browser_config = BrowserConfig(
        headless=True,  
        verbose=True,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
        ),
        proxy_config=ProxyConfig(server="http://192.168.50.150:7890")
    )
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=page_url,
                config=run_config
            )
            content = result.markdown
            #   LOG.info(f"{content}")
            # 提取网页中与问题相关的片段
            summary = extract_relevant_context(query, content, page_url)
            result = f"### {page_url} content:\n{summary}"
            return result
    except Exception as e:
        LOG.error(f"Crawl Page {page_url} fails: {e}")
        return str(e)  
    

async def searxng_search(query: str, language: str, time_range: str):
    # http://127.0.0.1:8080/search?format=json&q=广州天气&language=zh-CN&time_range=&safesearch=0&categories=general

    searxng_url = os.getenv("SEARXNG_URL") or "http://127.0.0.1:8088"
    global search_max_results

    links = []
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            url = f"{searxng_url}/search?format=json&q={query}&language={language}&time_range={time_range}&safesearch=0&categories=general"
            async with session.get(url ) as response:
                results = (await response.json())["results"]
                links = [result["url"] for result in results[: search_max_results]]
                LOG.info(f"searxng_search results:{results}")
    except Exception as e:
        LOG.error(f"Web search error: {e}")

    return links

@fc_register("tool")
def LLMWorker(input: str):
    """
    A pretrained LLM like yourself. Useful when you need to act with general world knowledge and common sense. Prioritize it when you are confident in solving the problem yourself. Input can be any instruction.

    Args:
        input (str): instruction
    """
    try:
        llm = lazyllm.OnlineChatModule(stream=False)
        query = f"Respond in short directly with no extra words.\n\n{input}"
        response = llm(query, llm_chat_history=[])
        return response
    except Exception as e:
        LOG.error(f"LLMWorker error: {e}")

def log(msg):
    print(f"183- msg:\n{msg}")
    return msg

def build_web_search_agent():
    with pipeline() as ppl:
        # ppl.log = log

        # 将query扩充为任务描述
        ppl.formarter = lambda query: PROMPT_TEMPLATE.format(query=query) 

        ppl.agent = ReactAgent(
                llm=lazyllm.OnlineChatModule(source='uniin', enable_thinking=False, stream=False),
                tools=['WebSearchTool', 'CrawlPagesTool'],
                return_trace=True,
                max_retries=10,
            )
        """         
        这一步的目的是从前面组件的输出中提取最终答案。因为 agent 的回复可能包含中间推理过程或其他多余文本，这个操作确保只提取出最终答案部分（在 `"Answer:"` 之后的内容）。如果没有 `"Answer:"` 标记，则保留原始输出不变。
        """

        # ppl.log = log

        ppl.clean = lazyllm.ifs(lambda x: "Answer:" in x, lambda x: x.split("Answer:")[-1], lambda x:x)

    return ppl

