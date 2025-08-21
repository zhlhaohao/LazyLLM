import os
import lazyllm
import json
import queue
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from .web_search import build_web_search_agent
from lazyllm import pipeline, ActionModule, ChatPrompter, bind, globals, LOG
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
from .web_search import (
    agent_source,
    agent_model,
    agent_en_model,
    llm_max_workers,
    max_tokens,
)
from .util import (
    chunk_content,
    extract_between_braces,
    merge_args,
    read_file,
    lazy_trace,
    fake_report,
)

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


def translate_segment(segment, index):
    if index > 0:  # 只有第1个线程才能输出
        globals._init_sid()

    return lazyllm.OnlineChatModule(
        source=agent_source,
        model=agent_en_model,
        stream=True,
        enable_thinking=False,
    )(TRANSLATE_PROMPT.format(context=segment))


def summary_keypoint(key_point, context, index):
    if index > 0:  # 只有第1个线程才能输出
        globals._init_sid()

    prompt = KEYPOINT_SUMMARY_PROMPT.format(context=context, key_point=key_point)

    ans = lazyllm.OnlineChatModule(
        source=agent_source, model=agent_model, enable_thinking=False, stream=True
    )(prompt)

    return ans

def translate_summary(summary):
    # 判断语言
    segments = chunk_content(summary, 500)
    # segments = output
    language = lazyllm.OnlineChatModule(
        source=agent_source, model=agent_model, enable_thinking=False, stream=True
    )(LANGUAGE_PROMPT.format(context=segments[0]))
    language = language.strip()

    if not language.startswith("zh"):
        lazy_trace(msg="将原文报告翻译成中文", is_clear=True)
        LOG.info("106- 翻译成中文")
        results = []
        with lazyllm.ThreadPoolExecutor(max_workers=llm_max_workers) as executor:
            translate_futures = [
                executor.submit(translate_segment, segment, index) for index, segment in enumerate(segments)
            ]
            for future in translate_futures:
                ans = future.result()
                results.append(ans)

        translated = "\n\n".join(results)
        return summary + "\n\n# 译文如下：\n\n" + translated
    else:
        return summary


def save_report(content):
    output_dir = os.path.expanduser(os.path.join(lazyllm.config["log_dir"], "report"))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            output_dir, f"{globals['memory']['topic']}-{timestamp}.md"
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        LOG.info(f"Report saved to {filename}")


def make_report(input):
    """
    一次性总结，输出量较少
    """
    try:
        summary = lazyllm.OnlineChatModule(
            source=agent_source,
            model=agent_model,
            enable_thinking=False,
            stream=True,
            static_params={
                "temperature": 0.6,
                "max_tokens": max_tokens,
            },
        ).prompt(ChatPrompter(instruction=SUMMARY_PROMPT))(input)

        LOG.info(f"113- 总结已生成:\n\n{summary}")
        final_report = translate_summary(summary)
        save_report(final_report)
        return final_report
    except Exception as ex:
        LOG.error(f"217- Error: {ex}")
        return "报告生成失败！"


def make_long_report(context):
    """
    全文分关键要点总结
    """
    lazy_trace(msg="资料已经收集完成，开始生成报告", is_clear=True)
    LOG.info("194- 开始生成报告")

    if (
        "processed_count" in globals["memory"]
        and globals["memory"]["processed_count"] < 10
    ):
        return make_report(context)

    try:
        # views = read_file("keypoints.md")
        views = lazyllm.OnlineChatModule(
            source=agent_source,
            model=agent_model,
            enable_thinking=False,
            stream=True,
            static_params={
                "temperature": 0.6,
                "max_tokens": max_tokens,
            },
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
        #     with ThreadPoolExecutor(max_workers=llm_max_workers) as executor:
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

        with lazyllm.ThreadPoolExecutor(max_workers=llm_max_workers) as executor:
            futures = []
            for i, view in enumerate(views):
                view_name = view.get(
                    "view",
                    f"view{i + 1}",
                )

                output.append(f"## {i + 1}. {view_name}")
                future = executor.submit(summary_keypoint, view_name, context, i)
                futures.append(
                    (future, len(output))
                )  # Store future and its position in output list
                output.append("")  # Placeholder for the result

            for future, index in futures:
                ans = future.result()
                output[index] = ans

        summary = "\n\n".join(output)
        LOG.info(f"345- 总结已生成:\n\n{summary}")
        final_report = translate_summary(summary)
        save_report(final_report)
        return final_report
    except Exception as ex:
        LOG.error(f"63- Error: {ex}")
        return "报告生成失败! 大模型上下文长度不够，请减少研究深度，或改用英语查询"


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
        # ppl.fake = fake_report
        ppl.input_data = format_input
        ppl.expand_prompt = expand_prompt | bind(input_data=ppl.input_data)
        ppl.expand_query = lazyllm.OnlineChatModule(
            source=agent_source, model=agent_model, enable_thinking=False, stream=True
        )
        ppl.transform_queries = transform_queries | bind(input_data=ppl.input_data)
        ppl.web_search = lazyllm.warp(web_search, _concurrent=False)
        ppl.merge = merge_args
        ppl.make_long_report = make_long_report

    return ppl

main_ppl = build_research_agent()
_thread_limiter = Semaphore(2)

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
    msg_queue = queue.Queue()
    result_container = [None]

    def worker():
        with _thread_limiter:
            with lazyllm.ThreadPoolExecutor(1) as executor:
                future = executor.submit(
                    main_ppl,
                    json.dumps(
                        {"query": query, "language": language, "depth": depth},
                        ensure_ascii=False,
                    ),
                )
                # 必须放在submit之后，否则sid不确定
                globals["memory"] = {
                    "topic": query,
                    "processed_count": 0,
                    "processed_urls": [],
                }

                llm_log = ""
                trace_log = ""
                while True:
                    if value := lazyllm.FileSystemQueue().dequeue():
                        trace_log = ""
                        llm_log += "".join(value)
                        msg_queue.put("/log:" + llm_log)

                    elif (
                        value := lazyllm.FileSystemQueue()
                        .get_instance("lazy_trace")
                        .dequeue()
                    ):
                        llm_log = ""
                        trace_log = "".join(value)
                        msg_queue.put(f"/log:{trace_log}")

                    elif future.done():
                        break

                answer = future.result()
                result_container[0] = f"<FINAL_ANSWER>{answer}"

    thread = threading.Thread(target=worker)
    thread.start()

    while True:
        try:
            msg = msg_queue.get(timeout=0.5)
            await ctx.sample(msg)
        except queue.Empty:
            if not thread.is_alive():
                break

    thread.join()
    answer = result_container[0]
    # LOG.info(f"\n\n最终回答:\n\n{answer}")
    return answer


"""
研究课题：Privacy-Preserving Mechanisms in Multi-Access Edge Computing (MEC) Environments
语言：en
研究深度：1

Technology & Innovation:
1. "Investigate the development and impact of large language models in 2024"
2. "Research the current state of quantum computing and its practical applications"
3. "Analyze the evolution and future of edge computing technologies"
4. "Explore the latest advances in brain-computer interface technology"
5. Privacy-Preserving Mechanisms in Multi-Access Edge Computing (MEC) Environments
6. Research on AI-Based Anomaly Traffic Detection in 5G Core Networks

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
    query = "Privacy-Preserving Mechanisms in Multi-Access Edge Computing (MEC) Environments"
    query_json = json.dumps(
        {"query": query, "language": "en", "depth": 1}, ensure_ascii=False
    )

    # 命令行界面
    # ans = ActionModule(main_ppl).start()(
    #     query_json,
    # )
    # print(f"最终回答:\n{ans}")
    globals["memory"]["topic"] = query
    with lazyllm.ThreadPoolExecutor(1) as executor:
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
        ppl.report = make_long_report

    result = ActionModule(ppl).start()(content)
    LOG.info(f"340- 报告已生成:\n\n{result}")


if __name__ == "__main__":
    # test_detail_report()
    main()
