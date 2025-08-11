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


# 示例使用
if __name__ == "__main__":
    sample_content = """
This is a short English sentence.

这是一个比较短的中文句子。

This is another English paragraph with a bit more text. It describes something interesting that might need to be grouped with others.

这是另一段中文内容。它包含多个句子来测试中文字符的计数和分段逻辑。我们希望它能正确地与前后内容合并或分离。

Short line.
短行。

Very long paragraph consisting of many English words and sentences that go on and on to exceed the minimum word count requirement by a large margin. This should form its own chunk even without merging with others. Let's make sure it's long enough. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

最后的中文段落用于测试结尾情况。
"""

    chunks = chunk_content(sample_content, min_words=30)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1} (Word Count: {count_words(chunk)}):\n{chunk}\n{'-' * 50}")