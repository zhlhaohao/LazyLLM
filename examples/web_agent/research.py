import lazyllm
import json
import asyncio
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, AlpacaPrompter, ChatPrompter, bind, LOG
from .prompts import RESEARH_PROMPT

expand_query_prompt = """You are an expert research assistant. Given the user's query, generate up to 1 distinct, precise search queries that would help gather comprehensive information on the topic. If the user requests a specific language, please include it in the response, defaulting to zh-CN.
CRITICAL: You must answer in this JSON format

EXAMPLE JSON OUTPUT:
{{
    "queries": [
        "query1",
        "query2"
    ],
    "language": "en"
}}


query:\n{query}
"""

def log(*args):
    print(f"16- log:")
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
    return [json.dumps({"query": query, "language": language},ensure_ascii=False) for query in queries]

def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        return "出现错误，无相关新闻资料返回"

def build_research_agent():
    with pipeline() as ppl:
        # 扩充query到N个querys
        ppl.expand_query = lazyllm.OnlineChatModule('uniin').prompt(AlpacaPrompter(expand_query_prompt))
        ppl.log1 = log

        ppl.transform_queries = lambda input: transform_queries(input)
        # ppl.log2 = log

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)        
        # ppl.log3 = log

        ppl.merge = merge_args
        # ppl.log4 = log


        ppl.formatter = (
            lambda input, query: dict(
                context_str=input, query=query,
            ) 
        ) | bind(query=ppl.input)

        ppl.summary = lazyllm.OnlineChatModule('uniin', enable_thinking=False).prompt(ChatPrompter(instruction=RESEARH_PROMPT))

    return ppl

if __name__ == '__main__':
    
    # prompter = AlpacaPrompter(instruction=expand_query_prompt)
    # res = prompter.generate_prompt("台湾基隆潮境公园有哪些餐厅，用繁体中文")
    # print(res)

    query = "美元利息与黄金价格走势的关系"
    # query = "俄乌战争截至2025年7月的最新情报，请搜索英语资料"
    # query = "本月华盛顿有什么政治新闻，用英语"
    # query = "2025年好莱坞新片的评价，请搜索英文资料"
    # query = "香港黄丝回流率统计，并给出回流的前5个原因，最后给出一个真实的事例"
    # query = "请提供俄罗斯人对中国人的看法，用俄语"
    main_ppl = build_research_agent()
    ans = ActionModule(main_ppl).start()(query)
    print(f"最终回答:\n{ans}")