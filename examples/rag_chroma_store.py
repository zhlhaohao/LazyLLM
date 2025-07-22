"""
@test_store.py @rag_milvus_store.py
写一个基于lazyllm的ai agent。
1. 请仔细阅读 rag_milvus_store.py 的源码，基于他的业务逻辑开发,但是取消rerank环节
2. 将向量库从milvus 改造成 chroma ，存储持久化到 {workspace folder}/.chroma 目录下
3. 如果chroma持久化存储文件不存在，则创建并将document目录下的所有文件进行向量化和持久化保存
4. 关于 chroma的编程方法，请参考 test_store.py
5. 使用 OnlineChatModule 的qwen 模型作为问答
6. 使用 QwenEmbedding 作为嵌入模型
7. 要将文件名和路径保存为元数据
8. 检索的结果除了chunk字段外，还必须包含文件名和路径
9. 运行本程序，输入问题，得到回答，回答中必须说明答案来自于哪些文件
"""

# -*- coding: utf-8 -*-

import os
import lazyllm
from lazyllm import bind, config
from lazyllm.tools.rag import DocField, DataType
import shutil


class TmpDir:
    def __init__(self):
        self.root_dir = os.path.expanduser(
            os.path.join("/home/lianghao/github/LazyLLM", ".data")
        )
        self.rag_dir = os.path.join(self.root_dir, "rag_master")
        os.makedirs(self.rag_dir, exist_ok=True)
        self.chroma_dir = os.path.join(self.root_dir, "chroma")


tmp_dir = TmpDir()

# 配置Chroma存储
chroma_store_conf = {
    "type": "chroma",
    "kwargs": {
        "dir": tmp_dir.chroma_dir,
    },
}

# 配置文档字段（包含文件名和路径）
doc_fields = {
    "filename": DocField(data_type=DataType.VARCHAR, max_size=256, default_value=""),
    "file_path": DocField(data_type=DataType.VARCHAR, max_size=1024, default_value=""),
}

# 初始化嵌入模型
embedding_model = lazyllm.OnlineEmbeddingModule("qwen")

# 初始化文档模块
documents = lazyllm.Document(
    dataset_path=tmp_dir.rag_dir,
    embed=embedding_model,
    manager=False,
    store_conf=chroma_store_conf,
    doc_fields=doc_fields,
)

# 创建Node Group，将文档分割为句子
documents.create_node_group(
    name="sentences", transform=lambda s: s.split("\n") if s else ""
)

documents._impl.store.update()

# 初始化检索器
retriever = lazyllm.Retriever(
    doc=documents,
    group_name="sentences",
    similarity="cosine",
    output_format="content",  # 输出格式是字符串，而不是node(chunk)对象
    topk=30,
)

# 初始化Qwen模型
chat_model = lazyllm.OnlineChatModule(model="qwen")

# 构建提示模板
prompt = (
    "你将扮演一个人工智能问答助手的角色，完成一项对话任务。"
    "在这个任务中，你需要根据给定的上下文以及问题，给出你的回答。"
)

# 构建LLM模块
llm = chat_model.prompt(
    lazyllm.ChatPrompter(instruction=prompt, extra_keys=["context_str"])
)

with lazyllm.pipeline() as ppl:
    # 检索
    ppl.retriever = retriever

    def logger(ret):
        print(ret)
        return ret

    ppl.logger = logger

    # 格式化检索结果
    ppl.formatter = (
        lambda nodes, query: dict(context_str=",".join(nodes), query=query)
    ) | bind(query=ppl.input)

    # 生成回答
    ppl.llm = llm

if __name__ == "__main__":
    try:
        rag = lazyllm.ActionModule(ppl)
        rag.start()
        res = rag("什么是ai agent？")
        print(f"answer: {res}")
    finally:
        # 清理临时目录
        # shutil.rmtree(tmp_dir.root_dir)
        pass
