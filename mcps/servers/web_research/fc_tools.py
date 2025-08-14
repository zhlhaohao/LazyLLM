import asyncio
import json
import os
import aiohttp
import random
import lazyllm
from datetime import datetime
from lazyllm import ModuleBase, fc_register, pipeline, OnlineChatModule, LOG
from lazyllm.tools.agent import ToolAgent
from typing import List
from .prompts import AGENT_PROMPT, EXTRACT_PROMPT
from urllib.parse import quote
import concurrent.futures

# Create a thread pool (you can define this at module level or class level)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

agent_source = os.environ.get("AGENT_SOURCE", "qwen")
agent_model = os.environ.get("AGENT_MODEL", "qwen3-32b")
agent_en_model = os.environ.get("AGENT_EN_MODEL", "qwen3-32b")
search_max_results = 100

@fc_register("tool")
def WebSearchTool(query: str, language: str = "zh-CN", time_range: str = ""):
    """Worker that search web pages using searxng, input should be a query.
    Args:
        query (str): query, not original query.
        language (str, optional): language code of the query.
        time_range (str): When `time_range` is set to "year", it indicates that the user wants to query news for this year. It can also take the values "month", "week", or "day". The default value is "".
    """

    async def worker(query: str, language: str, time_range: str):
        searxng_url = os.getenv("SEARXNG_URL") or "http://127.0.0.1:8088"
        global search_max_results

        links = []
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                query = quote(query, safe="")
                url = f"{searxng_url}/search?format=json&q={query}&language={language}&time_range={time_range}&safesearch=0&categories=general"
                async with session.get(url) as response:
                    results = (await response.json())["results"]
                    links = [result["url"] for result in results[:search_max_results]]
                    for result in results[:search_max_results]:
                        msg = f"{result['engine']} - {result['title']} - {result['url']}\n"

                        # lazy-trace 检索出的网站
                        lazyllm.FileSystemQueue.get_instance("lazy_trace").enqueue(msg)
                        LOG.debug(f"搜索链接:{msg}")

        except Exception as e:
            LOG.error(f"Web search error: {e}")

        return links

    return asyncio.run(worker(query, language, time_range))


# class CrawlPages(ModuleBase):
#     """
#     主要是为了测试reture_trace=True的情况，在作为工具被调用的情况下，由于线程id，无法实现在主程序中被捕获,还需要继续研究源码
#     """

#     def __init__(self, return_trace: bool = False):
#         super().__init__(return_trace=return_trace)

#     def forward(self, page_url_list, relevant_content, valid_threshold, language):
#         try:
#             result = asyncio.run(
#                 crawl_many_pages(
#                     page_url_list, relevant_content, valid_threshold, language
#                 )
#             )
#             return result
#         except Exception as e:
#             LOG.error(f"67- CrawlPagesTool error: {str(e)}")
#             return str(e)


# @fc_register("tool")
# def CrawlPagesTool(
#     page_url_list: List[str],
#     relevant_content: str,
#     valid_threshold: int = 5,
#     language: str = "zh-CN",
# ):
#     """
#     Worker that crawl web page contents. Input should be a list of page url.

#     Args:
#         page_url_list (List[str]): list of page url to crawl.
#         relevant_content (str): relevant_content.
#         valid_threshold (int): valid threshold
#         language (str, optional): language code of the query.
#     """
#     return CrawlPages(return_trace=False)(
#         page_url_list, relevant_content, valid_threshold, language
#     )


@fc_register("tool")
def CrawlPagesTool(
    page_url_list: List[str],
    relevant_content: str,
    valid_threshold: int = 5,
    language: str = "zh-CN",
):
    """
    Worker that crawl web page contents. Input should be a list of page url.

    Args:
        page_url_list (List[str]): list of page url to crawl.
        relevant_content (str): relevant_content.
        valid_threshold (int): valid threshold.
        language (str, optional): language code of the query.
    """
    result = asyncio.run(
        crawl_many_pages(page_url_list, relevant_content, valid_threshold, language)
    )
    return result


async def crawl_many_pages(
    page_url_list: List[str], relevant_content: str, valid_threshold: int, language: str
):
    # crawl4ai爬取url的内容，询问大模型词网页是否有用，有用则返回与用户提问相关的片段
    # 每次处理batch_size个URL，直到处理的项目数量超过valid_threshold
    try:
        batch_size = 5
        if valid_threshold < batch_size:
            batch_size = valid_threshold

        semaphore = asyncio.Semaphore(batch_size)
        processed_count = 0  # 记录已处理的项目数量
        iteration_contexts = []

        async def process_link_with_sem(link):
            async with semaphore:
                return await crawl_single_page(link, relevant_content, language)

        # 分批处理，每批batch_size个URL
        for i in range(0, len(page_url_list), batch_size):
            # 如果已处理的项目数量超过max_processed，则停止处理
            if processed_count >= valid_threshold:
                break

            # 获取当前批次的URL
            batch_urls = page_url_list[i : i + batch_size]

            # 每个批次的任务间隔1秒启动
            async def delayed_task(index, link):
                await asyncio.sleep(index * 1)
                return await process_link_with_sem(link)

            # 创建当前批次的任务
            tasks = [
                asyncio.wait_for(delayed_task(j, link), timeout=1200)
                for j, link in enumerate(batch_urls)
            ]

            # 执行当前批次的任务
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_results = [
                res for res in batch_results if not isinstance(res, Exception)
            ]

            # 处理当前批次的结果
            for res in batch_results:
                if res and "Web content is irrelevant" not in res:
                    iteration_contexts.append(res)

            # 更新已处理的项目数量
            processed_count = len(iteration_contexts)
            LOG.info(f"157- 共成功获取{processed_count}个相关网页内容")

        content = "\n\n".join(iteration_contexts)
        return f"<FINAL_ANSWER>{content}"
    except Exception as e:
        LOG.error(f"168- Crawl Pages error: {e}")
        return str(e)


MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 2000))


# 返回网页内容上与问题有关的片段
def extract_relevant_context(query, page_text, page_url, language):
    prompt = EXTRACT_PROMPT.format(
        query=query,
        page_text=page_text[:20000],
        context_length=MAX_CONTEXT_LENGTH,
        current_date=get_current_date_us_full(),
        page_url=page_url,
    )
    model = agent_model
    if language != "zh-CN":
        model = agent_en_model

    try:
        result = OnlineChatModule(
            source=agent_source, model=model, stream=True, enable_thinking=False
        )(prompt, llm_chat_history=[])
        return result
    except Exception as e:
        LOG.error(e)
        return str(e)


def get_current_date_us_full():
    today = datetime.now()
    return today.strftime("%B %d, %Y")


async def crawl_single_page(page_url: str, relevant_content: str, language: str):
    """Firecrawl爬取网页的内容

curl -X POST http://10.119.101.21:9860/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
      "url": "https://www.zaobao.com/news/china/story20250513-6328924",
      "onlyMainContent": true,
      "formats" : ["markdown"]
    }'

    Args:
        url (_type_): url

    Returns:
        _type_: _description_
    """
    urls = []
    if os.getenv("FIRECRAWL_URL"):
        urls.append(os.getenv("FIRECRAWL_URL"))
    if os.getenv("FIRECRAWL_URL_1"):
        urls.append(os.getenv("FIRECRAWL_URL_1"))

    firecrawl_url = random.choice(urls)
    # LOG.info(f"firecrawl_url: {firecrawl_url}")
    full_url = f"{firecrawl_url}v1/scrape"

    headers = {
        "Content-Type": "application/json",
    }
    param = {
        "url": page_url,
        "formats": ["markdown"],
        "onlyMainContent": True,
        "waitFor": 2000,
        "timeout": 30000,
    }

    try:
        LOG.info(f"开始爬取{page_url}")
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(full_url, json=param, timeout=30) as resp:
                LOG.info(f"爬取结束{page_url}")
                if resp.status == 200:
                    resp = await resp.text()
                    data = json.loads(resp).get("data")
                    content = data.get("markdown")
                    LOG.info(f"235- 抽取网页:{page_url}")

                    summary = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        extract_relevant_context,
                        relevant_content,
                        content,
                        page_url,
                        language,
                    )

                    if (
                        summary
                        and isinstance(summary, str)
                        and "Web content is irrelevant" not in summary
                    ):
                        LOG.info(f"239- 网页内容 :{page_url}:有{len(summary)}字")
                        result = f"# [{data.get('metadata').get('title', page_url)}]({page_url}) Content:\n\n{summary}"

                        # 清空trace队列然后写入网页摘要
                        queue = lazyllm.FileSystemQueue.get_instance("lazy_trace")
                        queue.clear()
                        queue.enqueue(result)
                        return result
                    else:
                        LOG.info(f"247- 网页内容:{page_url}:无有效内容")
                        return ""
                else:
                    text = await resp.text()
                    LOG.info(f"292--爬取网页失败:{page_url}:{resp.status} - {text}")
                    return None
    except Exception as e:
        LOG.error(f"210-爬取网页失败:{page_url}:{str(e)}")
        return str(e)


def log(msg):
    print(f"183- msg:\n{msg}")
    return msg

def build_web_search_agent():
    with pipeline() as ppl:
        # ppl.log = log
        # 将query扩充为任务描述
        ppl.format = lambda query: AGENT_PROMPT.format(query=query)

        ppl.agent = ToolAgent(
            llm=lazyllm.OnlineChatModule(
                source=agent_source,
                model=agent_model,
                enable_thinking=False,
                return_trace=False,
                stream=True,
            ),
            tools=["WebSearchTool", "CrawlPagesTool"],
            return_trace=False,
            max_retries=10,
        )

    return ppl

