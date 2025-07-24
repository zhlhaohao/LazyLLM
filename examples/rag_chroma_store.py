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

import os
from lazyllm import (
    bind,
    Document,
    OnlineEmbeddingModule,
    Retriever,
    ChatPrompter,
    OnlineChatModule,
    pipeline,
    ActionModule,
)
from lazyllm.tools.rag.global_metadata import RAG_DOC_FILE_NAME


def info(msg):
    print(f"26- logger:{msg}")
    return msg


class TmpDir:
    def __init__(self):
        self.root_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", ".data")
        )

        self.rag_dir = os.path.join(self.root_dir, "documents")
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

# 定义需要保存哪些meta data
# doc_fields = {
#     "filename": DocField(data_type=DataType.VARCHAR, max_size=256, default_value=""),
# }

# 嵌入模型
# embedding_model = OnlineEmbeddingModule("qwen")
embedding_model = OnlineEmbeddingModule(
    source="openai",
    embed_model_name=os.getenv("EMBED_MODEL_NAME"),
    embed_url=os.getenv("EMBED_URL"),
    api_key=os.getenv("EMBED_API_KEY"),
)

# 对话模型
chat_model = OnlineChatModule(source="uniin", model="qwen3-32b", stream=True)
# chat_model = OnlineChatModule(source="qwen", stream=True)

# 排除某些文件和目录
def exclude_reader(file):
    return []


Document.register_global_reader("**/another/*", exclude_reader)


# 初始化文档模块
documents = Document(
    dataset_path=tmp_dir.rag_dir,
    embed=embedding_model,
    manager=False,
    store_conf=chroma_store_conf,
    # doc_fields=doc_fields,
)

# 创建Node Group，将文档分割为句子
documents.create_node_group(
    name="sentences", transform=lambda s: s.split("\n") if s else ""
)

# documents._impl.store.update()

# 初始化检索器
retriever = Retriever(
    doc=documents,
    group_name="sentences",
    similarity="bm25_chinese",
    # output_format="content",  # 输出格式是字符串，而不是node(chunk)对象
    topk=30,
)


# 构建提示模板
prompt = (
    "你将扮演一个人工智能问答助手的角色，完成一项对话任务。"
    "在这个任务中，你需要根据给定的上下文以及问题，给出你的回答,请在回答中说明答案来自于哪些文件:\n\n{context_str}\n/no_think"
)

# 构建LLM模块


llm = chat_model.prompt(ChatPrompter(instruction=prompt))


def get_context(nodes):
    """
    @examples/rag_chroma_store.py 请阅读<AI_PROMPT> 的指示，然后在其下方开始编程
    1. 遍历 nodes
    2. content = node.get_content()
    3. filename = node.global_metadata.get(RAG_DOC_FILE_NAME, "")
    4. 按照 filename 分组，将文件名相同的内容组合在一起，格式为  ## {filename} \n {content}
    5. 组合成一个字符串返回
    """
    from collections import defaultdict

    file_content = defaultdict(list)

    # 按文件名分组
    for node in nodes:
        filename = node.global_metadata.get(RAG_DOC_FILE_NAME, "")
        if filename:
            file_content[filename].append(node.get_content())

    # 组合格式化字符串
    result = ""
    for filename, contents in file_content.items():
        result += f"## {filename} \n{', '.join(contents)}\n\n"

    return result.strip()


with pipeline() as ppl:
    # 检索
    ppl.retriever = retriever

    # 将检索结果（nodes）转换为字符串,context_str是自定义的key，而query是ChatPrompter内置的，代表用户的问题
    # 最终返回一个字典，喂给llm，而llm用prompt指定了ChatPrompter-自动将这个字典转换为最终的prompt，并返回给llm
    ppl.formatter = (
        lambda input, query: dict(
            context_str=get_context(nodes=input),
            query=query,
        )
    ) | bind(query=ppl.input)

    # 打印formatter的输出结果
    ppl.logger = info

    # 生成回答
    ppl.llm = llm

if __name__ == "__main__":
    rag = ActionModule(ppl)
    rag.start()
    res = rag("如何用ai制作ppt？")
    print(f"answer: {res}")
