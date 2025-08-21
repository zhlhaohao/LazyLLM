import os
from datetime import datetime
import time
import lazyllm

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
                current_chunk += "\n\n" + segment
                current_word_count += segment_word_count
            else:
                current_chunk = segment
                current_word_count = segment_word_count

    # 添加最后一个块（即使它小于min_words）
    if current_chunk:
        result.append(current_chunk)

    return result


def merge_args(*args):
    res = []
    for i, arg in enumerate(args, 1):
        res.append(arg)
    text = "\n\n".join(res)
    return text


def read_file(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_md_path = os.path.join(current_dir, "sample", filename)
    try:
        with open(data_md_path, "r", encoding="utf-8") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File not found: {data_md_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None



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


def get_current_date_us_full():
    today = datetime.now()
    return today.strftime("%B %d, %Y")


def contains_chinese(text: str) -> bool:
    """
    Detect if a string contains UTF-8 Chinese characters.

    Args:
        text (str): The string to check for Chinese characters.

    Returns:
        bool: True if the string contains Chinese characters, False otherwise.
    """
    if not isinstance(text, str):
        return False

    for char in text:
        # Check if character is in the range of Chinese Unicode blocks
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False


def lazy_trace(msg, is_clear=False):
    queue = lazyllm.FileSystemQueue.get_instance("lazy_trace")
    if is_clear:
        queue.clear()
    queue.enqueue(msg)


def print_result_in_segments(content: str, segments: int = 5):
    """
    Split the result into specified number of segments and print each segment with 1-second interval
    """
    # Split the result into lines to avoid breaking words
    lines = content.split("\n")

    # Calculate approximate lines per segment
    lines_per_segment = len(lines) // segments

    for i in range(segments):
        # Determine the start and end indices for this segment
        start_idx = i * lines_per_segment
        # For the last segment, include all remaining lines
        end_idx = (i + 1) * lines_per_segment if i < segments - 1 else len(lines)

        # Extract the segment
        segment_lines = lines[start_idx:end_idx]
        segment = "\n".join(segment_lines)

        lazy_trace(segment)
        if i < segments - 1:
            time.sleep(1)


def fake_report(msg):
    content = read_file("report.md")
    print_result_in_segments(content, 10)

    return content
