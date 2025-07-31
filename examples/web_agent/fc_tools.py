import asyncio
import lazyllm
from lazyllm import fc_register, ReWOOAgent, deploy, pipeline, bind
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import aiohttp
import os
from lazyllm import LOG
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from lazyllm.tools.agent import ReactAgent
from .utils import extract_relevant_context

search_max_results = 5


PROMPT_TEMPLATE = """
你是一位资深研究人员和资深记者，需要基于用户给定的问题从网络上收集信息，经过专业的整理、分析和总结，回答用户问题。
你的工作流程如下：

1. 判断根据问题是否可直接得出答案
   - 如果用户问题可以直接回答，无需网络查询，则直接输出结果。
   - 如果不足以回答，则先进行必要的网络查询。

2. 进行网络查询
   - 你需要将用户问题调用对应工具从网络得到url list。
   - 将url list进行爬取，如果获取了详细的资料可直接回答，否则则重新执行步骤2。

3. 对网络查询结果进行解析和整理，得到用户问题的答案

4. 错误处理
   - 如果出现错误则重新执行，直到成功。


问题：
{query}

"""


@fc_register("tool")
def CrawlPagesWorker(page_url_list: List[str], query: str):
    """
    Worker that crawl web page contents. Input should be a list of page url.

    Args:
        page_url_list (List[str]): list of page url to crawl.
        query (str): user query.
    """
    return asyncio.run(crawl_pages(page_url_list, query))


async def crawl_pages(page_url_list: List[str], query: str):
    # crawl4ai爬取url的内容，询问大模型词网页是否有用，有用则返回与用户提问相关的片段
    # 创建信号量限制并发数为3,一个批次启动3个任务
    semaphore = asyncio.Semaphore(5)

    async def process_link_with_sem(link):
        async with semaphore:
            return await crawl_page(link, query)

    # 每个批次的任务间隔1秒启动
    async def delayed_task(index, link):
        await asyncio.sleep(index * 1)
        return await process_link_with_sem(link)

    # 创建所有任务批次,开始执行
    tasks = [
        asyncio.wait_for(delayed_task(i, link), timeout=20)
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


async def crawl_page(page_url: str, query: str):
    browser_config = BrowserConfig(
        headless=True,  
        verbose=True,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
        )
    )
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=page_url,
                config=run_config
            )
            content = result.markdown.fit_markdown
            #   LOG.info(f"{content}")
            # 提取网页中与问题相关的片段
            content = extract_relevant_context(query, content)
            return content
    except Exception as e:
      return str(e)  
    

@fc_register("tool")
def WebSearchWorker(query: str):
    """Worker that search web pages using searxng, input should be a query.

    Args:
        query (str): user query.    
    """
    return asyncio.run(searxng_search(query))

async def searxng_search(query: str):
    # http://127.0.0.1:8080/search?format=json&q=广州天气&language=zh-CN&time_range=&safesearch=0&categories=general

    searxng_url = os.getenv("SEARXNG_URL") or "http://127.0.0.1:8080"
    global search_max_results

    links = []
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{searxng_url}/search?format=json&q={query}&language=zh-CN&time_range=&safesearch=0&categories=general"
            ) as response:
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
    llm = lazyllm.OnlineChatModule(stream=False)
    query = f"Respond in short directly with no extra words.\n\n{input}"
    response = llm(query, llm_chat_history=[])
    return response


def build_web_search_agent():
    with pipeline() as ppl:
        # 将query扩充为任务描述
        ppl.formarter = lambda query: PROMPT_TEMPLATE.format(query=query) 

        ppl.agent = ReactAgent(
                llm=lazyllm.OnlineChatModule(source='uniin', model="qwen3-32b", enable_thinking=False, stream=False),
                tools=['WebSearchWorker', 'CrawlPagesWorker', 'LLMWorker'],
                return_trace=True,
                max_retries=3,
            )
        """         
        这一步的目的是从前面组件的输出中提取最终答案。因为 agent 的回复可能包含中间推理过程或其他多余文本，这个操作确保只提取出最终答案部分（在 `"Answer:"` 之后的内容）。如果没有 `"Answer:"` 标记，则保留原始输出不变。
        """
        ppl.clean = lazyllm.ifs(lambda x: "Answer:" in x, lambda x: x.split("Answer:")[-1], lambda x:x)

    return ppl

