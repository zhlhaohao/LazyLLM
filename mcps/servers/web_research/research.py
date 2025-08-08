import lazyllm
import json
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, LOG
from .prompts import RESEARH_PROMPT, EXPAND_QUERY_PROMPT, SUMMARY_PROMPT
import os
from typing import Annotated, List
from fastmcp import Context
from pydantic import Field

def log(*args):
    print("16- log:")
    for i, arg in enumerate(args, 1):
        print(f"  arg{i}: {arg}")
    return args if len(args) > 1 else args[0] if args else None


def merge_args(*args):
    res = []
    for i, arg in enumerate(args, 1):
        res.append(arg)
    text = "\n\n".join(res)
    return text


def transform_queries(queries, input_data):
    queries = json.loads(queries)["queries"]

    result = [
        json.dumps(
            {
                "query": query,
                "relevant_content": input_data["query"],
                "language": input_data["language"],
                "valid_threshold": input_data["valid_threshold"],
                # "expand_query_count": input_data["expand_query_count"],
            },
            ensure_ascii=False,
        )
        for query in queries
    ]
    return result


def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        return "出现错误，无相关新闻资料返回"


def format_input(input):
    data = json.loads(input)
    depth = data.get("depth")
    if depth == 1:
        valid_threshold = 3
        expand_query_count = 1
    elif depth == 2:
        valid_threshold = 5
        expand_query_count = 2
    elif depth == 3:
        valid_threshold = 5
        expand_query_count = 3
    elif depth == 4:
        valid_threshold = 5
        expand_query_count = 5
    elif depth == 5:
        valid_threshold = 10
        expand_query_count = 5
    else:
        valid_threshold = 5
        expand_query_count = 3
    return {
        "query": data["query"],
        "language": data["language"],
        "valid_threshold": valid_threshold,
        "expand_query_count": expand_query_count,
    }


def expand_prompt(_, input_data):
    return EXPAND_QUERY_PROMPT.format(
        query=input_data["query"], expand_query_count=input_data["expand_query_count"]
    )


def build_research_agent():
    with pipeline() as ppl:
        ppl.input_data = format_input
        # ppl.log1 = log

        ppl.expand_prompt = expand_prompt | bind(input_data=ppl.input_data)
        ppl.expand_query = lazyllm.OnlineChatModule("qwen", stream=False)
        ppl.transform_queries = transform_queries | bind(input_data=ppl.input_data)

        ppl.log2 = log

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)
        # ppl.log3 = log

        ppl.merge = merge_args

        # ppl.formatter = (
        #     lambda input, query: dict(
        #         context_str=input,
        #         query=query,
        #     )
        # ) | bind(query=ppl.input)
        # ppl.log4 = log

        ppl.summary = lazyllm.OnlineChatModule("qwen", enable_thinking=False).prompt(
            ChatPrompter(instruction=SUMMARY_PROMPT)
        )

    return ppl

async def web_research(
    query: Annotated[str, Field(description="user's query, do not change")],
    language: Annotated[
        str, Field(description="language code of research, default to zh-CN")
    ] = "zh-CN",
    depth: Annotated[int, Field(description="depth of research, default to 3")] = 3,
    ctx: Context = None,
) -> str:
    """
    search the web and do research works to answer user's query
    """
    main_ppl = build_research_agent()
    with lazyllm.ThreadPoolExecutor(1) as executor:
        future = executor.submit(
            main_ppl,
            json.dumps(
                {"query": query, "language": language, "depth": depth},
                ensure_ascii=False,
            ),
        )
        buffer = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                buffer += "".join(value)
                await ctx.sample("llm:" + buffer)
            elif (
                value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
            ):
                msg = "".join(value)
                await ctx.sample(f"trace:{msg}")
                LOG.info(f"\n\ntrace:\n{msg}")
            elif future.done():
                break

        answer = future.result()
        LOG.info(f"\n\n最终回答:\n\n{answer}")
        return f"<FINAL_ANSWER>{answer}"
    return "失败"


if __name__ == "__main__":
    # prompter = AlpacaPrompter(instruction=expand_query_prompt)
    # res = prompter.generate_prompt("台湾基隆潮境公园有哪些餐厅，用繁体中文")
    # print(res)

    # query = "美元利息与黄金价格走势的关系"
    # query = "伯尔尼本周有什么政治、宗教、治安方面的新闻，用英语"
    # query = "本月华盛顿有什么政治新闻，用英语"
    # query = "2025年8月，广州的天气情况"
    # query = "请分析芬太尼的化学结构，与吗啡 杜冷丁进行比较,用英语"
    query = "电视剧 扫毒风暴 ，各个主演的评价分析"
    # query = "请提供俄罗斯人对中国人的看法，用俄语"
    main_ppl = build_research_agent()

    ans = ActionModule(main_ppl).start()(
        json.dumps(
            {"query": query, "language": "zh-CN", "depth": 2},
            ensure_ascii=False,
        )
    )
    print(f"最终回答:\n{ans}")

    # with lazyllm.ThreadPoolExecutor(1) as executor:
    #     future = executor.submit(main_ppl, query)
    #     buffer = ""
    #     while True:
    #         if value := lazyllm.FileSystemQueue().dequeue():
    #             buffer += "".join(value)
    #             print(f"\n\n流式输出:\n{buffer}")
    #         elif (
    #             value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
    #         ):
    #             print(f"\n\n中间跟踪:\n{''.join(value)}")
    #         elif future.done():
    #             break
    #     print(f"\n\n最终回答:\n{future.result()}")
