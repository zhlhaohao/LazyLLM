import lazyllm
import json
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, LOG
from .prompts import RESEARH_PROMPT, EXPAND_QUERY_PROMPT
import os
from typing import Annotated, List
from fastmcp import Context
from pydantic import Field

def log(*args):
    LOG.info("16- log:")
    for i, arg in enumerate(args, 1):
        print(f"  arg{i}: {arg}")
    return args if len(args) > 1 else args[0] if args else None


def merge_args(*args):
    res = []
    for i, arg in enumerate(args, 1):
        res.append(arg)
    text = "\n\n".join(res)
    return text


def transform_queries(input):
    source_obj = json.loads(input)
    queries = source_obj.get("queries", [])
    language = source_obj.get("language", "zh-CN")
    return [
        json.dumps({"query": query, "language": language}, ensure_ascii=False)
        for query in queries
    ]


def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        return "出现错误，无相关新闻资料返回"


def build_research_agent():
    with pipeline() as ppl:
        # 扩充query到N个querys
        ppl.prompt = lambda input: EXPAND_QUERY_PROMPT.format(
            query=input, expand_query_count=os.getenv("EXPAND_QUERY_COUNT", 3)
        )

        ppl.expand_query = lazyllm.OnlineChatModule("uniin")
        ppl.log1 = log

        ppl.transform_queries = lambda input: transform_queries(input)
        # ppl.log2 = log

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)
        # ppl.log3 = log

        ppl.merge = merge_args
        # ppl.log4 = log

        ppl.formatter = (
            lambda input, query: dict(
                context_str=input,
                query=query,
            )
        ) | bind(query=ppl.input)

        ppl.summary = lazyllm.OnlineChatModule("uniin", enable_thinking=False).prompt(
            ChatPrompter(instruction=RESEARH_PROMPT)
        )

    return ppl

async def web_research(
    query: Annotated[str, Field(description="user's query, do not change")],
    ctx: Context,
) -> str:
    """
    search web and summarize to answer user query
    """
    main_ppl = build_research_agent()
    with lazyllm.ThreadPoolExecutor(1) as executor:
        future = executor.submit(main_ppl, query)
        buffer = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                buffer += "".join(value)
                await ctx.sample("log:" + buffer)
            elif (
                value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
            ):
                LOG.info(f"\n\n中间跟踪:\n{''.join(value)}")
            elif future.done():
                break

        answer = future.result()
        LOG.info(f"\n\n最终回答:\n{answer}")
        # await ctx.sample(answer)
        return answer
    return "失败"


if __name__ == "__main__":
    # prompter = AlpacaPrompter(instruction=expand_query_prompt)
    # res = prompter.generate_prompt("台湾基隆潮境公园有哪些餐厅，用繁体中文")
    # print(res)

    # query = "美元利息与黄金价格走势的关系"
    # query = "伯尔尼本周有什么政治、宗教、治安方面的新闻，用英语"
    # query = "本月华盛顿有什么政治新闻，用英语"
    # query = "2025年好莱坞新片的评价，请搜索英文资料"
    query = "请分析芬太尼的化学结构，与吗啡 杜冷丁进行比较"
    # query = "请提供俄罗斯人对中国人的看法，用俄语"
    main_ppl = build_research_agent()

    # ans = ActionModule(main_ppl).start()(query)
    # print(f"最终回答:\n{ans}")

    with lazyllm.ThreadPoolExecutor(1) as executor:
        future = executor.submit(main_ppl, query)
        buffer = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                buffer += "".join(value)
                print(f"\n\n流式输出:\n{buffer}")
            elif (
                value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
            ):
                print(f"\n\n中间跟踪:\n{''.join(value)}")
            elif future.done():
                break
        print(f"\n\n最终回答:\n{future.result()}")
