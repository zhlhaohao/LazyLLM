import asyncio
import json
import os
import aiohttp
import lazyllm
from datetime import datetime
from lazyllm import fc_register, pipeline, OnlineChatModule, LOG
from lazyllm.tools.agent import ToolAgent
from typing import List
from .prompts import AGENT_PROMPT, EXTRACT_PROMPT


agent_source = os.environ.get("AGENT_SOURCE", "qwen")
agent_model = os.environ.get("AGENT_MODEL", "qwen")
search_max_results = 100

@fc_register("tool")
def WebSearchTool(query: str, language: str = "zh-CN", time_range: str = ""):
    """Worker that search web pages using searxng, input should be a query.

    Args:
        query (str): query, not original query.
        language (str, optional): language code of the query.
        time_range (str): [year|month|week|day], time range of the search. time_range=year when query contains "this year", time_range=month when query contains "this month", time_range=week when query contains "this week", time_range=day when query contains "today".
    """

    async def worker(query: str, language: str, time_range: str):
        searxng_url = os.getenv("SEARXNG_URL") or "http://127.0.0.1:8088"
        global search_max_results

        links = []
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                url = f"{searxng_url}/search?format=json&q={query}&language={language}&time_range={time_range}&safesearch=0&categories=general"
                async with session.get(url) as response:
                    results = (await response.json())["results"]
                    links = [result["url"] for result in results[:search_max_results]]
                    LOG.debug(f"searxng_search results:{results}")
        except Exception as e:
            LOG.error(f"Web search error: {e}")

        return links

    return asyncio.run(worker(query, language, time_range))


@fc_register("tool")
def CrawlPagesTool(
    page_url_list: List[str], relevant_content: str, valid_threshold: int = 5
):
    """
    Worker that crawl web page contents. Input should be a list of page url.

    Args:
        page_url_list (List[str]): original page_url_list from web search tool.
        relevant_content (str): relevant_content.
        valid_threshold (int): valid threshold
    """
    # print(f"\n\n66- user_ask:\n\n{user_ask}")
    result = asyncio.run(
        crawl_many_pages(page_url_list, relevant_content, valid_threshold)
    )
    # print(f"120- 爬取网页内容:\n{result}")
    return result


async def crawl_many_pages(
    page_url_list: List[str], relevant_content: str, valid_threshold: int
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
                return await crawl_single_page(link, relevant_content)

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
                asyncio.wait_for(delayed_task(j, link), timeout=120)
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

        content = "\n\n".join(iteration_contexts)
        return f"<FINAL_ANSWER>{content}"
    except Exception as e:
        LOG.error(f"Crawl Pages error: {e}")
        return str(e)


MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 2000))


# 返回网页内容上与问题有关的片段
def extract_relevant_context(query, page_text, page_url):
    prompt = EXTRACT_PROMPT.format(
        query=query,
        page_text=page_text,
        context_length=MAX_CONTEXT_LENGTH,
        current_date=get_current_date_us_full(),
        page_url=page_url,
    )
    result = OnlineChatModule(
        source=agent_source, model=agent_model, stream=False, enable_thinking=False
    )(prompt, llm_chat_history=[])
    return result


def get_current_date_us_full():
    today = datetime.now()
    return today.strftime("%B %d, %Y")


async def crawl_single_page(page_url: str, relevant_content: str):
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
    firecrawl_url = os.getenv("FIRECRAWL_URL", "")

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
                    result = json.loads(resp)
                    content = result.get("data").get("markdown")
                    # 提取网页中与问题相关的片段
                    summary = extract_relevant_context(relevant_content, content, page_url)
                    result = f"### {page_url} content:\n{summary}"
                    return result
                else:
                    text = await resp.text()
                    LOG.info(
                        f"204-Error fetching webpage text with Firecrawl: {resp.status} - {text}"
                    )
                    return None
    except Exception as e:
        LOG.error(f"210-Error fetching webpage text with Firecrawl:{e}")
        return None


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
                stream=False,
                return_trace=True,
            ),
            tools=["WebSearchTool", "CrawlPagesTool"],
            return_trace=False,
            max_retries=10,
        )

    return ppl

