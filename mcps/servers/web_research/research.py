import lazyllm
import json
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, LOG
from .prompts import EXPAND_QUERY_PROMPT, SUMMARY_PROMPT, TRANSLATE_PROMPT
from typing import Annotated
from fastmcp import Context
from pydantic import Field
from .fc_tools import agent_source, agent_model, agent_en_model

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

def extract_between_braces(text):
    first_brace_start = text.find("{")
    last_brace_end = text.rfind("}")
    if (
        first_brace_start != -1
        and last_brace_end != -1
        and first_brace_start < last_brace_end
    ):
        ret = text[first_brace_start : last_brace_end + 1]
        return ret
    else:
        return text

def transform_queries(expanded_queries, input_data):
    obj = json.loads(extract_between_braces(expanded_queries))

    result = [
        json.dumps(
            {
                "query": query,
                "relevant_content": obj["translated_query"],
                "language": input_data["language"],
                "valid_threshold": input_data["valid_threshold"],
            },
            ensure_ascii=False,
        )
        for query in obj["queries"]
    ]
    return result


def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        LOG.error(e)
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
    prompt = EXPAND_QUERY_PROMPT.format(
        query=input_data["query"],
        expand_query_count=input_data["expand_query_count"],
        language=input_data["language"],
    )
    return prompt

def summary(input, input_data):
    language = input_data["language"]

    LOG.info(f"104- 生成总结\n\n{input}")
    summary = lazyllm.OnlineChatModule(
        source=agent_source,
        model=agent_model if language == "zh-CN" else agent_en_model,
        enable_thinking=False,
        stream=True,
    ).prompt(ChatPrompter(instruction=SUMMARY_PROMPT))(input)

    LOG.info(f"113- 总结输出\n\n{summary}")

    if language == "zh-CN":
        return summary
    else:
        LOG.info("106- 翻译成中文")
        prompt = TRANSLATE_PROMPT.format(context=summary)
        transcript = lazyllm.OnlineChatModule(
            source=agent_source,
            model=agent_en_model,
            stream=True,
            enable_thinking=False,
        )(prompt)
        return summary + "\n\n" + transcript


def build_research_agent(language):
    with pipeline() as ppl:
        ppl.input_data = format_input
        # ppl.log2 = log

        ppl.expand_prompt = expand_prompt | bind(input_data=ppl.input_data)

        ppl.expand_query = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        )
        ppl.transform_queries = transform_queries | bind(input_data=ppl.input_data)

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=True)

        ppl.merge = merge_args

        # ppl.summary = lazyllm.OnlineChatModule(
        #     source=agent_source,
        #     model=agent_model if language == "zh-CN" else agent_en_model,
        #     enable_thinking=False,
        #     stream=True,
        # ).prompt(ChatPrompter(instruction=SUMMARY_PROMPT))

        ppl.summary = summary | bind(input_data=ppl.input_data)

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
    main_ppl = build_research_agent(language)
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
    language = "en"

    # query = "美元利息与黄金价格走势的关系"
    # query = "伯尔尼本周有什么政治、宗教、治安方面的新闻，用英语"
    # query = "本月华盛顿有什么政治新闻，用英语"
    # query = "2025年8月，广州的天气情况"
    query = "2025年市场上减肥药竞争格局"
    # query = "电视剧 扫毒风暴 ，各个主演的评价分析"
    # query = "分析今年(2025)以来中国军队高层的腐败查处情况和重点下马人物"

    # # 图形化界面
    # lazyllm.WebModule(main_ppl, port=20012).start().wait()
    #

    query_json = json.dumps(
        {"query": query, "language": language, "depth": 1}, ensure_ascii=False
    )
    main_ppl = build_research_agent(language)

    # 命令行界面
    ans = ActionModule(main_ppl).start()(
        query_json,
    )
    print(f"最终回答:\n{ans}")

    # with lazyllm.ThreadPoolExecutor(1) as executor:
    #     future = executor.submit(
    #         main_ppl,
    #         query_json,
    #     )
    #     buffer = ""
    #     while True:
    #         if value := lazyllm.FileSystemQueue().dequeue():
    #             buffer += "".join(value)
    #             print("llm:" + buffer)
    #         elif (
    #             value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
    #         ):
    #             msg = "".join(value)
    #             print(f"trace:{msg}")
    #             LOG.info(f"\n\ntrace:\n{msg}")
    #         elif future.done():
    #             break

    #     answer = future.result()
    #     LOG.info(f"\n\n最终回答:\n\n{answer}")
    #     print(f"<FINAL_ANSWER>{answer}")
