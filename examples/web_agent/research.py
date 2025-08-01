import lazyllm
import json
import asyncio
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, AlpacaPrompter, ChatPrompter, bind, LOG
from .prompts import RESEARH_PROMPT

expand_query_prompt = """You are an expert research assistant. Given the user's query, generate up to 2 distinct, precise search queries in chinese that would help gather comprehensive information on the topic.
Return only a Python list of strings, for example: ["query1", "query2", "query3"].
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

def build_research_agent():
    with pipeline() as ppl:
        # 扩充query到N个querys
        ppl.expand_query = lazyllm.OnlineChatModule('uniin').prompt(AlpacaPrompter(expand_query_prompt))

        # ppl.log1 = log
        ppl.to_list = lambda output: json.loads(output)
        ppl.log2 = log

        def web_search(query):
            try:
                agent = build_web_search_agent()
                return agent.start()(query)
            except Exception as e:
                return "出现错误，无相关新闻资料返回"

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)        
        # ppl.log3 = log

        ppl.merge = merge_args

        ppl.formatter = (
            lambda input, query: dict(
                context_str=input, query=query,
            ) 
        ) | bind(query=ppl.input)

        ppl.summary = lazyllm.OnlineChatModule('uniin', enable_thinking=False).prompt(ChatPrompter(instruction=RESEARH_PROMPT))

    return ppl

if __name__ == '__main__':
    
    # prompter = AlpacaPrompter(instruction=expand_query_prompt)
    # res = prompter.generate_prompt('如何评价周杰伦')
    # print(res)

    # query = "俄乌战争截至2025年7月的最新情报，请搜索英语资料"
    # query = "中国限制稀土供应，美国有什么应对措施，估计多久能够摆脱中国的稀土依赖，请搜索英语资料"
    # query = "2025年好莱坞新片的评价，请搜索英文资料"
    query = "台湾基隆潮境公园有哪些餐厅"
    main_ppl = build_research_agent()
    ans = ActionModule(main_ppl).start()(query)
    print(f"最终回答:\n{ans}")