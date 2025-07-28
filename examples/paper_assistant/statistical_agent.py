import lazyllm
from lazyllm import pipeline
from lazyllm.tools.agent import ReactAgent

from .utils import bi_tools

def log(input):
    print(f"statistic- input:{input}")
    return input


# 通过流水线方式实现ReactAgent，它有2个工具供调用：1. run_sql_query-自然语言查询数据库 2. run_code-运行代码
# 用户输入问题，agent对问题进行思考，调用sql query查询结果并调用run_code运行代码，得到结果例如生成图表返回
def build_statistical_agent():
    with pipeline() as sql_ppl:

        # 将用户的问题，扩充为一个对资深数据科学家的任务描述
        sql_ppl.formarter = lambda query: bi_tools.BI_PROMPT.format(query=query, image_path="./images") 
        sql_ppl.log = log

        sql_ppl.agent = ReactAgent(
                llm=lazyllm.OnlineChatModule(source='uniin', model="qwen3-235b-a22b", stream=False),
                tools=['run_code', 'run_sql_query'],
                return_trace=True,
                max_retries=3,
            )
        sql_ppl.clean = lazyllm.ifs(lambda x: "Answer:" in x, lambda x: x.split("Answer:")[-1], lambda x:x)

    return sql_ppl


if __name__ == "__main__":
    main_ppl = build_statistical_agent()
    lazyllm.WebModule(main_ppl, port=20012, static_paths="./images").start().wait()