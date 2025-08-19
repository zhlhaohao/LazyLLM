import os
import lazyllm
import json
from concurrent.futures import ThreadPoolExecutor
from .fc_tools import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, LOG
from .prompts import (
    EXPAND_QUERY_PROMPT,
    SUMMARY_PROMPT,
    TRANSLATE_PROMPT,
    EXPAND_QUERY_PROMPT_ZH,
    KEYPOINT_PROMPT,
    KEYPOINT_SUMMARY_PROMPT,
    LANGUAGE_PROMPT,
)
from typing import Annotated
from fastmcp import Context
from pydantic import Field
from .fc_tools import agent_source, agent_model, agent_en_model
from .util import chunk_content, extract_between_braces, merge_args, read_file


def log(*args):
    print("16- log:")
    for i, arg in enumerate(args, 1):
        print(f"  arg{i}: {arg}")
    return args if len(args) > 1 else args[0] if args else None


def transform_queries(expanded_queries, input_data):
    try:
        obj = json.loads(extract_between_braces(expanded_queries))

        result = [
            json.dumps(
                {
                    "query": query,
                    "relevant_content": obj["translated_query"]
                    if input_data["language"] != "zh-CN"
                    else input_data["query"],
                    "language": input_data["language"],
                    "valid_threshold": input_data["valid_threshold"],
                },
                ensure_ascii=False,
            )
            for query in obj["queries"]
        ]

        LOG.info(f"59- 扩充到多个关联查询:{result}")
        return result
    except Exception as ex:
        LOG.error(f"63- Error: {ex}")
        raise ex


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


def translate_segment(segment):
    return lazyllm.OnlineChatModule(
        source=agent_source,
        model=agent_en_model,
        stream=True,
        enable_thinking=False,
    )(TRANSLATE_PROMPT.format(context=segment))


def summary_keypoint(key_point, context):
    prompt = KEYPOINT_SUMMARY_PROMPT.format(context=context, key_point=key_point)

    ans = lazyllm.OnlineChatModule(
        source=agent_source, model=agent_model, enable_thinking=False, stream=True
    )(prompt)

    return ans


def summary(input, input_data):
    """
    一次性总结，输出量较少
    """
    language = input_data["language"]

    try:
        LOG.info(f"104- 生成总结\n\n{input}")
        max_tokens = 8192
        if os.getenv("MAX_TOKENS"):
            max_tokens = int(os.getenv("MAX_TOKENS"))

        summary = lazyllm.OnlineChatModule(
            source=agent_source,
            model=agent_model if language == "zh-CN" else agent_en_model,
            enable_thinking=False,
            stream=True,
            static_params={
                "temperature": 0.6,
                "max_tokens": max_tokens,
            },  # "max_tokens": 30000
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
    except Exception as ex:
        LOG.error(f"217- Error: {ex}")
        return "深度研究报告生成失败！"


def detail_summary(context):
    """
    全文分关键要点总结
    """
    try:
        # views = read_file("keypoints.md")
        views = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        ).prompt(ChatPrompter(instruction=KEYPOINT_PROMPT))(context)
        views = json.loads(extract_between_braces(views)).get("views", [])

        output = []
        # for i, view in enumerate(views):
        #     view_name = view.get(
        #         "view",
        #         f"view{i + 1}",
        #     )

        #     key_points = view.get("key_points", [])
        #     output.append(f"## {view_name}")
        #     with ThreadPoolExecutor(max_workers=4) as executor:
        #         futures = []
        #         for key_point in key_points:
        #             output.append(f"### {key_point}")
        #             # Submit the summary_keypoint function to the thread pool
        #             future = executor.submit(summary_keypoint, key_point, context)
        #             futures.append(
        #                 (future, len(output))
        #             )  # Store future and its position in output list
        #             output.append("")  # Placeholder for the result

        #         # Collect results as they complete
        #         for future, index in futures:
        #             ans = future.result()
        #             output[index] = (
        #                 ans  # Fill in the placeholder with the actual result
        #             )

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i, view in enumerate(views):
                view_name = view.get(
                    "view",
                    f"view{i + 1}",
                )

                output.append(f"## {view_name}")
                # Submit the summary_keypoint function to the thread pool
                future = executor.submit(summary_keypoint, view_name, context)
                futures.append(
                    (future, len(output))
                )  # Store future and its position in output list
                output.append("")  # Placeholder for the result

            for future, index in futures:
                ans = future.result()
                output[index] = ans

        summary = "\n\n".join(output)
        LOG.info(f"345- 总结已生成:\n\n{summary}")

        # 判断语言
        segments = chunk_content(summary, 500)
        # segments = output
        language = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        )(LANGUAGE_PROMPT.format(context=segments[0]))
        language = language.strip()

        if not language.startswith("zh"):
            LOG.info("106- 翻译成中文")
            results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                translate_futures = [
                    executor.submit(translate_segment, segment) for segment in segments
                ]
                for future in translate_futures:
                    ans = future.result()
                    results.append(ans)

            translated = "\n\n".join(results)
            return summary + "\n\n# 译文如下：\n\n" + translated
        else:
            return summary

    except Exception as ex:
        LOG.error(f"63- Error: {ex}")
        return "报告生成失败!"


def web_search(query):
    try:
        agent = build_web_search_agent()
        return agent.start()(query)
    except Exception as e:
        LOG.error(e)
        return "出现错误，无相关资料返回"


def build_research_agent():
    """
    深度研究主线程
    """
    with pipeline() as ppl:
        ppl.input_data = format_input
        # ppl.log2 = log

        ppl.expand_prompt = expand_prompt | bind(input_data=ppl.input_data)
        ppl.expand_query = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        )
        ppl.transform_queries = transform_queries | bind(input_data=ppl.input_data)
        ppl.web_search = lazyllm.warp(
            web_search, _concurrent=False
        )  # 关闭多线程并发，确保有trace结果流式输出
        ppl.merge = merge_args
        # ppl.summary = summary | bind(input_data=ppl.input_data)
        ppl.detail_summary = detail_summary

    return ppl

main_ppl = build_research_agent()


# MCP Tool 入口
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
    with lazyllm.ThreadPoolExecutor(1) as executor:
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

        llm_log = ""
        trace_log = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                trace_log = ""
                llm_log += "".join(value)
                await ctx.sample("/log:" + llm_log)

            elif (
                value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
            ):
                llm_log = ""
                trace_log = "".join(value)
                await ctx.sample(f"/log:{trace_log}")

            elif future.done():
                break

        answer = future.result()
        LOG.info(f"\n\n最终回答:\n\n{answer}")
        return f"<FINAL_ANSWER>{answer}"
    return "失败"


"""
Technology & Innovation:
1. "Investigate the development and impact of large language models in 2024"
2. "Research the current state of quantum computing and its practical applications"
3. "Analyze the evolution and future of edge computing technologies"
4. "Explore the latest advances in brain-computer interface technology"

Environmental & Sustainability:
1. "Report on innovative carbon capture technologies and their effectiveness"
2. "Investigate the global progress in renewable energy adoption"
3. "Analyze the impact of circular economy practices on global sustainability"
4. "Research the development of sustainable aviation technologies"

Healthcare & Biotechnology:
1. "Explore the latest developments in CRISPR gene editing technology"
2. "Analyze the impact of AI on drug discovery and development"
3. "Investigate the evolution of personalized medicine approaches"
4. "Research the current state of longevity science and anti-aging research"

Societal Impact:
1. "Examine the effects of social media on democratic processes"
2. "Analyze the impact of remote work on urban development"
3. "Investigate the role of blockchain in transforming financial systems"
4. "Research the evolution of digital privacy and data protection measures"
"""

def main():
    """
    测试入口
    """
    query = "Analyze the impact of circular economy practices on global sustainability"
    query_json = json.dumps(
        {"query": query, "language": "en", "depth": 3}, ensure_ascii=False
    )

    # 命令行界面
    # ans = ActionModule(main_ppl).start()(
    #     query_json,
    # )
    # print(f"最终回答:\n{ans}")

    with lazyllm.ThreadPoolExecutor(10) as executor:
        future = executor.submit(
            main_ppl,
            query_json,
        )

        buffer = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                buffer += "".join(value)
                # print("llm:" + buffer)
            elif (
                value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue()
            ):
                msg = "".join(value)
                LOG.info(f"lazy_trace:\n{msg}")
            elif future.done():
                break

        answer = future.result()
        LOG.info(f"\n\n最终回答:\n\n{answer}")
        print(f"<FINAL_ANSWER>{answer}")


def test_detail_report():
    """测试详细报告"""
    content = read_file("raw_data.md")
    # content = read_file("keypoints.md")
    if not content:
        return LOG.info("文件不存在")

    with pipeline() as ppl:
        ppl.detail_summary = detail_summary

    result = ActionModule(ppl).start()(content)
    LOG.info(f"340- 报告已生成:\n\n{result}")


if __name__ == "__main__":
    # test_detail_report()
    main()
