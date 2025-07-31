import lazyllm
import json
import asyncio
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, AlpacaPrompter, ChatPrompter, bind, LOG

expand_query_prompt = """You are an expert research assistant. Given the user's query, generate up to 2 distinct, precise search queries in chinese that would help gather comprehensive information on the topic.
Return only a Python list of strings, for example: ["query1", "query2", "query3"].
query:\n{query}
"""

summary_prompt = """你将扮演一个资深研究人员的角色,你需要根据给定的上下文以及问题，给出你的专业的分析研究报告:\n\ncontext:\n{context_str}\n\nquery:\n{query}"
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
            agent = build_web_search_agent()
            return agent.start()(query)

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)        
        # ppl.log3 = log

        ppl.merge = merge_args

        ppl.formatter = (
            lambda input, query: dict(
                context_str=input, query=query,
            ) 
        ) | bind(query=ppl.input)

        ppl.summary = lazyllm.OnlineChatModule('uniin', enable_thinking=False).prompt(ChatPrompter(instruction=summary_prompt))

    return ppl

if __name__ == '__main__':
    
    # prompter = AlpacaPrompter(instruction=expand_query_prompt)
    # res = prompter.generate_prompt('如何评价周杰伦')
    # print(res)

    query = "美元与黄金价格的关系是什么？"
    main_ppl = build_research_agent()
    ans = ActionModule(main_ppl).start()(query)
    print(f"最终回答:\n{ans}")