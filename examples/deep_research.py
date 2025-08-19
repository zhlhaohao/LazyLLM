# -*- coding: utf-8 -*-
# flake8: noqa: F821
"""
写一个基于lazyllm的ai agent。
1. 这是一个深度研究的agent ,需要经过N轮对话才能得到最终结论
2. 与llm的问答，采用 OnlineChatModule 的qwen模型
3. 通过 Loop实现多轮次对话
4. 第一轮对话的prompt必须包含：  这是深度研究的第1轮，一共需要进行5轮，你需要在此轮中给出计划
5. 最后一轮的prompt必须包含：这是深度研究的最后一轮，请给出最终结论
6. 中间的这几轮，prompt必须包含：这是深度研究的第i轮,一个有5轮，请根据前面的研究结果继续研究
7. prompt 必须包含前面所有轮次的回答历史，以  <history><turn>response1</turn><turn>response2</turn></hsitory>
8. prompt 的最后部分，必须是  <query>user's query</query>
9. 参考 rag_online.py 的写法，
10. 研究 flow.py 中的组件，适当使用 Pipeline \ Parallel \ Loop 等组件完成流程逻辑[DEEP RESEARCH][CODE MODE]
"""
import lazyllm
from lazyllm import ModuleBase, OnlineChatModule, LOG
from lazyllm.flow import (
    Pipeline,
    Loop,
)


class DeepResearchAgent(ModuleBase):
    def __init__(self, llm, total_rounds=3):
        super().__init__()
        self.llm = llm
        self.total_rounds = total_rounds
        self.history = []

        # 创建Pipeline处理每一轮的研究
        self.pipeline = Pipeline(self.build_prompt, self.llm, self.update_history)

        # 创建Loop组件用于控制多轮对话
        self.loop = Loop(
            self.pipeline, stop_condition=self.stop_condition, count=total_rounds
        )

    @property
    def round_num(self):
        """获取当前轮次"""
        return len(self.history) + 1

    def stop_condition(self, output):
        """循环条件判断"""
        return self.round_num > self.total_rounds

    # def loop_action(self, response):
    #     """执行一轮研究"""
    #     return self.pipeline(response)

    def build_prompt(self, output):
        """构建每一轮的prompt"""
        if self.round_num == 1:
            prompt = f"这是深度研究的第1轮，一共需要进行{self.total_rounds}轮，你需要在此轮中给出计划\n"
        elif self.round_num == self.total_rounds:
            prompt = "这是深度研究的最后一轮，请给出最终结论\n"
        else:
            prompt = f"这是深度研究的第{self.round_num}轮,一个有{self.total_rounds}轮，请根据前面的研究结果继续研究\n"

        # 添加历史记录
        prompt += "<history>\n"
        for i, response in enumerate(self.history):
            prompt += f"<turn>\n{response}\n</turn>"
        prompt += "</history>\n"

        # 添加用户查询
        prompt += "<query>什么是软实力</query>"
        prompt += "/no_think"
        return prompt

    def update_history(self, response):
        """更新历史记录"""
        self.history.append(response)
        return response

    def forward(self):
        """执行深度研究流程"""
        return self.loop("")


# 创建Qwen模型实例
qwen_model = OnlineChatModule(source="qwen")

# 创建深度研究Agent
# def deep_research_agent():
#     try:
#         return DeepResearchAgent(qwen_model).start()()
#     except Exception as e:
#         LOG.error(e)
#         return "出现错误，无相关资料返回"


# # 执行深度研究流程
# result = deep_research_agent()
# print("最终研究结果：", result)

with lazyllm.ThreadPoolExecutor(1) as executor:
    future = executor.submit(DeepResearchAgent(qwen_model))

    buffer = ""
    while True:
        if value := lazyllm.FileSystemQueue().dequeue():
            buffer += "".join(value)
            print("llm:" + buffer)
        elif value := lazyllm.FileSystemQueue().get_instance("lazy_trace").dequeue():
            msg = "".join(value)
            LOG.info(f"lazy_trace:\n{msg}")
        elif future.done():
            break

    answer = future.result()
    LOG.info(f"\n\n最终回答:\n\n{answer}")
    print(f"<FINAL_ANSWER>{answer}")
