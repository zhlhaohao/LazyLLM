from typing import Annotated
from pydantic import Field
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import lazyllm
from mcps.servers.web_research.web_search import (
    agent_source,
    agent_model,
)
prompt_classifier_template = """
## role：意图分类器
你是一个意图分类引擎，负责根据对话信息分析用户输入文本并确定唯一的意图类别。

## 限制:
你只需要回复意图的名字即可，不要额外输出其他字段，也不要进行翻译。

## 文本格式
输入文本为JSON格式，"human_input"中内容为用户的原始输入，"intent_list"为所有意图名列表

## 示例
User: {{"human_input": "生成研究报告，研究课题：Privacy-Preserving Mechanisms in Multi-Access Edge Computing Environments  语言：en  研究深度：1", "intent_list": ["生成研究报告", "搜索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  生成研究报告

User: {{"human_input": "梁浩和邓寅的联系方式是什么", "intent_list": ["生成研究报告", "检索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  通信录查询

User: {{"human_input": "融合平台研发室有多少员工，男员工多少人", "intent_list": ["生成研究报告", "检索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  通信录查询

User: {{"human_input": "请讲一个笑话", "intent_list": ["生成研究报告", "检索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  其它

User: {{"human_input": "知识库中关于休假的最新政策是什么", "intent_list": ["生成研究报告", "检索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  检索知识库

User: {{"human_input": "请阅读上传的文章，告诉我文章的主要讲了什么内容", "intent_list": ["生成研究报告", "检索知识库", "阅读文章", "AI编程", "通信录查询", "其它"]}}
Assistant:  阅读文章


输入文本如下:

{context}
"""  # noqa E501


async def intent_classifier(
    query: Annotated[str, Field(description="user query")],
) -> str:
  """analyzing user query and determining a unique intent category.
  """
  loop = asyncio.get_event_loop()
  with ThreadPoolExecutor() as executor:
      result = await loop.run_in_executor(executor, get_intent, query)
  return result

def get_intent(query):
  input = {
      "human_input": query,
      "intent_list": [
          "生成研究报告",
          "检索知识库",
          "阅读文章",
          "翻译文章",
          "通信录查询",
          "其它",
      ],
  }
  input = json.dumps(input, ensure_ascii=False)

  intent = lazyllm.OnlineChatModule(
      source=agent_source,
      model=agent_model,
      stream=False,
      enable_thinking=False,
  )(prompt_classifier_template.format(context=input))

  intent = intent.strip()
  return intent

async def main():
  query = "请阅读乔布斯传，告诉是苹果公司是什么时候成立的"
  loop = asyncio.get_event_loop()
  with ThreadPoolExecutor() as executor:
      result = await loop.run_in_executor(executor, get_intent, query)
  print(result)
  return result

if __name__ == "__main__":
  asyncio.run(main())





