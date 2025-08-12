import lazyllm
import json
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, LOG
from .prompts import (
    EXPAND_QUERY_PROMPT,
    SUMMARY_PROMPT,
    TRANSLATE_PROMPT,
    EXPAND_QUERY_PROMPT_ZH,
)
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
    try:
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

        LOG.info(f"59- web_search_queries:{result}")
        return result
    except Exception as ex:
        LOG.error(f"63- Error: {ex}")
        raise ex


def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        LOG.error(e)
        return "出现错误，无相关资料返回"


def format_input(input):
    data = json.loads(input)
    depth = data.get("depth")
    if depth == 1:
        valid_threshold = 2
        expand_query_count = 1
    elif depth == 2:
        valid_threshold = 3
        expand_query_count = 2
    elif depth == 3:
        valid_threshold = 3
        expand_query_count = 3
    elif depth == 4:
        valid_threshold = 5
        expand_query_count = 4
    elif depth == 5:
        valid_threshold = 8
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
    if input_data["language"] == "zh-CN":
        template = EXPAND_QUERY_PROMPT_ZH
    else:
        template = EXPAND_QUERY_PROMPT

    prompt = template.format(
        query=input_data["query"],
        expand_query_count=input_data["expand_query_count"],
        language=input_data["language"],
    )
    return prompt


def count_words(text: str) -> int:
    """计算文本中的“字数”：英文以空格分隔，中文每个字符算一个字。"""
    words = text.split()  # 按空白字符分割英文单词
    chinese_chars = sum(
        1 for char in text if "\u4e00" <= char <= "\u9fff"
    )  # 统计中文字符
    return len(words) + chinese_chars


def chunk_content(content: str, min_words: int = 50):
    """
    将文本内容分割成满足最小字数要求的段落块。

    Args:
        content (str): 输入的文本内容。
        min_words (int): 每个块所需的最小“字数”（默认为300）。

    Returns:
        List[str]: 满足条件的文本块列表。
    """

    # 按行分割内容
    segments = content.split("\n")
    segments = [seg.strip() for seg in segments if seg.strip()]  # 去除空白行和首尾空格

    if not segments:
        return []

    result = []
    current_chunk = ""
    current_word_count = 0

    for segment in segments:
        segment_word_count = count_words(segment)

        # 如果当前块不为空且加入当前段落后超过或等于最小字数，则检查是否应该分割
        if current_chunk and current_word_count >= min_words:
            # 当前块已满足要求，先保存
            result.append(current_chunk)
            current_chunk = segment
            current_word_count = segment_word_count
        else:
            # 否则合并到当前块
            if current_chunk:
                current_chunk += "\n" + segment
                current_word_count += segment_word_count
            else:
                current_chunk = segment
                current_word_count = segment_word_count

    # 添加最后一个块（即使它小于min_words）
    if current_chunk:
        result.append(current_chunk)

    return result


def summary(input, input_data):
    language = input_data["language"]

    LOG.info(f"104- 生成总结\n\n{input}")
    summary = lazyllm.OnlineChatModule(
        source=agent_source,
        model=agent_model if language == "zh-CN" else agent_en_model,
        enable_thinking=False,
        stream=True,
    ).prompt(ChatPrompter(instruction=SUMMARY_PROMPT))(input)

    LOG.info(f"113- 总结已生成:\n\n{summary}")

    if language == "zh-CN":
        return summary
    else:
        LOG.info("106- 翻译成中文")

        # Split input by newlines
        segments = chunk_content(summary, 500)
        results = []

        # Process each segment individually
        for segment in segments:
            if segment.strip():  # Only process non-empty segments
                translate_segment = lazyllm.OnlineChatModule(
                    source=agent_source,
                    model=agent_en_model,
                    stream=True,
                    enable_thinking=False,
                )(TRANSLATE_PROMPT.format(context=segment))
                results.append(translate_segment)

        combined_result = "\n".join(results)
        return summary + "\n\n" + combined_result


def build_research_agent(language):
    with pipeline() as ppl:
        ppl.input_data = format_input
        # ppl.log2 = log

        ppl.expand_prompt = expand_prompt | bind(input_data=ppl.input_data)

        ppl.expand_query = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        )

        ppl.transform_queries = transform_queries | bind(input_data=ppl.input_data)

        ppl.paralle_process = lazyllm.warp(web_search, _concurrent=False)

        ppl.merge = merge_args

        ppl.summary = summary | bind(input_data=ppl.input_data)

    return ppl


async def web_research(
    query: Annotated[str, Field(description="user's query")],
    language: Annotated[
        str, Field(description="language code of web search, default to zh-CN")
    ] = "zh-CN",
    depth: Annotated[
        int, Field(description="depth of research, from 1 through 5, default to 3")
    ] = 3,
    ctx: Context = None,
) -> str:
    """
    search the web and do research works to answer user's query
    """
    main_ppl = build_research_agent(language)
    with lazyllm.ThreadPoolExecutor(50) as executor:
        # 在submit执行的时候，获取协程或者线程id，初始化了_sid,这个sid就是FileSystemQueue的用于会话隔离的id值
        # 如果执行到这里的时候是处于协程模式下，那么只有同一个协程的代码才能共享消息队列
        # 如果执行到这里的时候是处于线程模式下，那么只有同一个线程的代码才能共享消息队列 --- 经实测，是线程模式
        # 由于__sid的值是ContextVar,可以通过线程复制给子协程，所以所有子协程都可以共享一个队列
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

            elif value := lazyllm.FileSystemQueue.get_instance("lazy_error").dequeue():
                LOG.error("".join(value))

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
    language = "zh-CN"

    # query = "美元利息与黄金价格走势的关系"
    # query = "伯尔尼本周有什么政治、宗教、治安方面的新闻，用英语"
    # query = "本月华盛顿有什么政治新闻，用英语"
    # query = "2025年8月，广州的天气情况"
    query = "agentic ai 的原理、实现和优秀的开源库"
    # query = "电视剧 扫毒风暴 ，各个主演的评价分析"
    # query = "分析今年(2025)以来中国军队高层的腐败查处情况和重点下马人物"

    # # 图形化界面
    # lazyllm.WebModule(main_ppl, port=20012).start().wait()
    #

    query_json = json.dumps(
        {"query": query, "language": language, "depth": 2}, ensure_ascii=False
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
