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

search_max_results = 5


PROMPT_TEMPLATE = """
你是一位资深研究人员和资深记者，需要基于用户给定的问题从网络上收集信息，经过专业的整理、分析和总结，回答用户问题。
你的工作流程如下：

1. 判断根据问题是否可直接得出答案
   - 如果用户问题可以直接回答，无需网络查询，则直接输出结果。
   - 如果不足以回答，则先进行必要的网络查询。

2. 进行网络查询
   - 识别用户想要查询哪个国家的资讯，将用户的问题翻译成该国家的语言。
   - 将用户问题调用搜索工具从网络得到url list。
   - 对url list调用爬虫工具进行网页爬取，获取详细的资料，如果资料已经收集完成则可直接回答。

3. 根据用户问题，对网络查询结果进行解析和整理，用简体中文回答。

4. 错误处理
   - 如果出现错误则退出。


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

    try:
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
    except Exception as e:
        LOG.error(f"Crawl Pages error: {e}")
        return str(e)

async def crawl_page(page_url: str, query: str):
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
            summary = extract_relevant_context(query, content)
            return summary
    except Exception as e:
        LOG.error(f"Crawl Single Page error: {e}")
        return str(e)  
    

@fc_register("tool")
def WebSearchWorker(query: str, language: str = "zh-CN"):
    """Worker that search web pages using searxng, input should be a query.

    Args:
        query (str): user query.    
        language (str, optional): language of the query. Defaults to "zh-CN". 

    Extra Info：
        All language codes list below
        'af', 'Afrikaans', '', 'Afrikaans'
        'ar', 'العربية', '', 'Arabic'
        'ar-SA', 'العربية', 'المملكة العربية السعودية', 'Arabic'
        'be', 'Беларуская', '', 'Belarusian'
        'bg', 'Български', '', 'Bulgarian'
        'bg-BG', 'Български', 'България', 'Bulgarian'
        'ca', 'Català', '', 'Catalan'
        'cs', 'Čeština', '', 'Czech'
        'cs-CZ', 'Čeština', 'Česko', 'Czech'
        'cy', 'Cymraeg', '', 'Welsh'
        'da', 'Dansk', '', 'Danish'
        'da-DK', 'Dansk', 'Danmark', 'Danish'
        'de', 'Deutsch', '', 'German'
        'de-AT', 'Deutsch', 'Österreich', 'German'
        'de-BE', 'Deutsch', 'Belgien', 'German'
        'de-CH', 'Deutsch', 'Schweiz', 'German'
        'de-DE', 'Deutsch', 'Deutschland', 'German'
        'el', 'Ελληνικά', '', 'Greek'
        'el-GR', 'Ελληνικά', 'Ελλάδα', 'Greek'
        'en', 'English', '', 'English'
        'en-AU', 'English', 'Australia', 'English'
        'en-CA', 'English', 'Canada', 'English'
        'en-GB', 'English', 'United Kingdom', 'English'
        'en-IE', 'English', 'Ireland', 'English'
        'en-IN', 'English', 'India', 'English'
        'en-NZ', 'English', 'New Zealand', 'English'
        'en-PH', 'English', 'Philippines', 'English'
        'en-PK', 'English', 'Pakistan', 'English'
        'en-SG', 'English', 'Singapore', 'English'
        'en-US', 'English', 'United States', 'English'
        'en-ZA', 'English', 'South Africa', 'English'
        'es', 'Español', '', 'Spanish'
        'es-AR', 'Español', 'Argentina', 'Spanish'
        'es-CL', 'Español', 'Chile', 'Spanish'
        'es-CO', 'Español', 'Colombia', 'Spanish'
        'es-ES', 'Español', 'España', 'Spanish'
        'es-MX', 'Español', 'México', 'Spanish'
        'es-PE', 'Español', 'Perú', 'Spanish'
        'et', 'Eesti', '', 'Estonian'
        'et-EE', 'Eesti', 'Eesti', 'Estonian'
        'eu', 'Euskara', '', 'Basque'
        'fa', 'فارسی', '', 'Persian'
        'fi', 'Suomi', '', 'Finnish'
        'fi-FI', 'Suomi', 'Suomi', 'Finnish'
        'fr', 'Français', '', 'French'
        'fr-BE', 'Français', 'Belgique', 'French'
        'fr-CA', 'Français', 'Canada', 'French'
        'fr-CH', 'Français', 'Suisse', 'French'
        'fr-FR', 'Français', 'France', 'French'
        'ga', 'Gaeilge', '', 'Irish'
        'gd', 'Gàidhlig', '', 'Scottish Gaelic'
        'gl', 'Galego', '', 'Galician'
        'he', 'עברית', '', 'Hebrew'
        'hi', 'हिन्दी', '', 'Hindi'
        'hr', 'Hrvatski', '', 'Croatian'
        'hu', 'Magyar', '', 'Hungarian'
        'hu-HU', 'Magyar', 'Magyarország', 'Hungarian'
        'id', 'Indonesia', '', 'Indonesian'
        'id-ID', 'Indonesia', 'Indonesia', 'Indonesian'
        'is', 'Íslenska', '', 'Icelandic'
        'it', 'Italiano', '', 'Italian'
        'it-CH', 'Italiano', 'Svizzera', 'Italian'
        'it-IT', 'Italiano', 'Italia', 'Italian'
        'ja', '日本語', '', 'Japanese'
        'ja-JP', '日本語', '日本', 'Japanese'
        'kn', 'ಕನ್ನಡ', '', 'Kannada'
        'ko', '한국어', '', 'Korean'
        'ko-KR', '한국어', '대한민국', 'Korean'
        'lt', 'Lietuvių', '', 'Lithuanian'
        'lv', 'Latviešu', '', 'Latvian'
        'ml', 'മലയാളം', '', 'Malayalam'
        'mr', 'मराठी', '', 'Marathi'
        'nb', 'Norsk Bokmål', '', 'Norwegian Bokmål'
        'nb-NO', 'Norsk Bokmål', 'Norge', 'Norwegian Bokmål'
        'nl', 'Nederlands', '', 'Dutch'
        'nl-BE', 'Nederlands', 'België', 'Dutch'
        'nl-NL', 'Nederlands', 'Nederland', 'Dutch'
        'pl', 'Polski', '', 'Polish'
        'pl-PL', 'Polski', 'Polska', 'Polish'
        'pt', 'Português', '', 'Portuguese'
        'pt-BR', 'Português', 'Brasil', 'Portuguese'
        'pt-PT', 'Português', 'Portugal', 'Portuguese'
        'ro', 'Română', '', 'Romanian'
        'ro-RO', 'Română', 'România', 'Romanian'
        'ru', 'Русский', '', 'Russian'
        'ru-RU', 'Русский', 'Россия', 'Russian'
        'sk', 'Slovenčina', '', 'Slovak'
        'sl', 'Slovenščina', '', 'Slovenian'
        'sq', 'Shqip', '', 'Albanian'
        'sv', 'Svenska', '', 'Swedish'
        'sv-SE', 'Svenska', 'Sverige', 'Swedish'
        'ta', 'தமிழ்', '', 'Tamil'
        'te', 'తెలుగు', '', 'Telugu'
        'th', 'ไทย', '', 'Thai'
        'th-TH', 'ไทย', 'ไทย', 'Thai'
        'tr', 'Türkçe', '', 'Turkish'
        'tr-TR', 'Türkçe', 'Türkiye', 'Turkish'
        'uk', 'Українська', '', 'Ukrainian'
        'ur', 'اردو', '', 'Urdu'
        'vi', 'Tiếng Việt', '', 'Vietnamese'
        'vi-VN', 'Tiếng Việt', 'Việt Nam', 'Vietnamese'
        'zh', '中文', '', 'Chinese'
        'zh-CN', '中文', '中国', 'Chinese'
        'zh-HK', '中文', '中國香港特別行政區', 'Chinese'
        'zh-TW', '中文', '台灣', 'Chinese'


    """
    return asyncio.run(searxng_search(query, language))

async def searxng_search(query: str, language: str):
    # http://127.0.0.1:8080/search?format=json&q=广州天气&language=zh-CN&time_range=&safesearch=0&categories=general

    searxng_url = os.getenv("SEARXNG_URL") or "http://127.0.0.1:8088"
    global search_max_results

    links = []
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            url = f"{searxng_url}/search?format=json&q={query}&language={language}&time_range=&safesearch=0&categories=general&ban_time_on_fail=5"
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
    print(f"msg:{msg}")
    return msg

def build_web_search_agent():
    with pipeline() as ppl:
        # ppl.log = log

        # 将query扩充为任务描述
        ppl.formarter = lambda query: PROMPT_TEMPLATE.format(query=query) 

        ppl.agent = ReactAgent(
                llm=lazyllm.OnlineChatModule(source='qwen', model="qwen3-32b", enable_thinking=False, stream=False),
                tools=['WebSearchWorker', 'CrawlPagesWorker', 'LLMWorker'],
                return_trace=True,
                max_retries=10,
            )
        """         
        这一步的目的是从前面组件的输出中提取最终答案。因为 agent 的回复可能包含中间推理过程或其他多余文本，这个操作确保只提取出最终答案部分（在 `"Answer:"` 之后的内容）。如果没有 `"Answer:"` 标记，则保留原始输出不变。
        """
        ppl.clean = lazyllm.ifs(lambda x: "Answer:" in x, lambda x: x.split("Answer:")[-1], lambda x:x)

    return ppl

