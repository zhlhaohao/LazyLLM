import random
from abc import ABC
from openai import OpenAI
import openai
import os
import json
import httpx
import logging
import time
import mcps.llm.chanhu_llm_sdk_python as cniin_llm
import ipaddress
from urllib.parse import urlparse

# Error message constants
ERROR_PREFIX = "**ERROR**"
ERROR_RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
ERROR_AUTHENTICATION = "AUTH_ERROR"
ERROR_INVALID_REQUEST = "INVALID_REQUEST"
ERROR_SERVER = "SERVER_ERROR"
ERROR_TIMEOUT = "TIMEOUT"
ERROR_CONNECTION = "CONNECTION_ERROR"
ERROR_MODEL = "MODEL_ERROR"
ERROR_CONTENT_FILTER = "CONTENT_FILTERED"
ERROR_QUOTA = "QUOTA_EXCEEDED"
ERROR_MAX_RETRIES = "MAX_RETRIES_EXCEEDED"
ERROR_GENERIC = "GENERIC_ERROR"

LENGTH_NOTIFICATION_CN = (
    "······\n由于大模型的上下文窗口大小限制，回答已经被大模型截断。"
)
LENGTH_NOTIFICATION_EN = "...\nThe answer is truncated by your chosen LLM due to its limitation on context length."


def clear_gen_conf(gen_conf):
    if "enable_cot" in gen_conf:
        gen_conf.pop("enable_cot")

    if "mcp_servers" in gen_conf:
        gen_conf.pop("mcp_servers")


def is_ip_address(base_url):
    try:
        # 尝试将字符串解析为IP地址
        if ipaddress.ip_address(base_url):
            return True
    except ValueError:
        # 如果解析失败，则表示不是IP地址，可能是域名
        return False


def extract_ip_from_url(base_url):
    # 解析URL
    parsed_url = urlparse(base_url)

    # 获取网络位置部分（即：'xxxx:9888'），不包括路径
    netloc = parsed_url.netloc

    # 如果包含端口号，则去掉端口号，只保留IP地址/域名部分
    if ":" in netloc:
        host = netloc.split(":")[0]
    else:
        host = netloc

    # 验证是否为IP地址
    try:
        if ipaddress.ip_address(host):
            return host
    except ValueError:
        # 不是IP地址，可能是域名
        return None


class Base(ABC):
    """所有模型对话接口的基类

    Args:
        ABC (_type_): _description_
    """

    def __init__(self, key, model_name, base_url):
        # F8080 - 代理设置
        timeout = int(os.environ.get("LM_TIMEOUT_SECONDS", 600))
        # 获取环境变量 SYSTEM_PROXY
        if (
            os.environ.get("SYSTEM_PROXY")
            and "host.docker.internal" not in base_url
            and "localhost" not in base_url
            and not is_ip_address(extract_ip_from_url(base_url))
        ):
            transport = httpx.HTTPTransport(proxy=os.environ.get("SYSTEM_PROXY"))
            self.client = OpenAI(
                http_client=httpx.Client(transport=transport),
                api_key=key,
                base_url=base_url,
                timeout=timeout,
            )
        else:
            self.client = OpenAI(api_key=key, base_url=base_url, timeout=timeout)

        self.model_name = model_name
        # Configure retry parameters
        self.max_retries = int(os.environ.get("LLM_MAX_RETRIES", 5))
        self.base_delay = float(os.environ.get("LLM_BASE_DELAY", 2.0))

    def _get_delay(self, attempt):
        """Calculate retry delay time"""
        return self.base_delay * (2**attempt) + random.uniform(0, 0.5)

    def _classify_error(self, error):
        """Classify error based on error message content"""
        error_str = str(error).lower()

        if (
            "rate limit" in error_str
            or "429" in error_str
            or "tpm limit" in error_str
            or "too many requests" in error_str
            or "requests per minute" in error_str
        ):
            return ERROR_RATE_LIMIT
        elif (
            "auth" in error_str
            or "key" in error_str
            or "apikey" in error_str
            or "401" in error_str
            or "forbidden" in error_str
            or "permission" in error_str
        ):
            return ERROR_AUTHENTICATION
        elif (
            "invalid" in error_str
            or "bad request" in error_str
            or "400" in error_str
            or "format" in error_str
            or "malformed" in error_str
            or "parameter" in error_str
        ):
            return ERROR_INVALID_REQUEST
        elif (
            "server" in error_str
            or "502" in error_str
            or "503" in error_str
            or "504" in error_str
            or "500" in error_str
            or "unavailable" in error_str
        ):
            return ERROR_SERVER
        elif "timeout" in error_str or "timed out" in error_str:
            return ERROR_TIMEOUT
        elif (
            "connect" in error_str
            or "network" in error_str
            or "unreachable" in error_str
            or "dns" in error_str
        ):
            return ERROR_CONNECTION
        elif (
            "quota" in error_str
            or "capacity" in error_str
            or "credit" in error_str
            or "billing" in error_str
            or "limit" in error_str
            and "rate" not in error_str
        ):
            return ERROR_QUOTA
        elif (
            "filter" in error_str
            or "content" in error_str
            or "policy" in error_str
            or "blocked" in error_str
            or "safety" in error_str
        ):
            return ERROR_CONTENT_FILTER
        elif (
            "model" in error_str
            or "not found" in error_str
            or "does not exist" in error_str
            or "not available" in error_str
        ):
            return ERROR_MODEL
        else:
            return ERROR_GENERIC

    def chat(self, system, history, gen_conf):
        if system:
            if not gen_conf.get("enable_cot"):
                system = system + "/no_think"
            else:
                system = system + "/think"
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]

        # 思维链输出开关处理
        extra_body = {}
        if "enable_cot" in gen_conf:
            if not gen_conf.get("enable_cot"):
                extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
        else:
            extra_body = {"chat_template_kwargs": {"enable_thinking": False}}

        clear_gen_conf(gen_conf)  # F8080
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=history,
                    extra_body=extra_body,
                    **gen_conf,
                )

                if any(
                    [
                        not response.choices,
                        not response.choices[0].message,
                        not response.choices[0].message.content,
                    ]
                ):
                    return "", 0
                ans = response.choices[0].message.content.strip()
                return ans, len(response)
            except Exception as e:
                # Classify the error
                error_code = self._classify_error(e)

                # Check if it's a rate limit error or server error and not the last attempt
                should_retry = (
                    error_code == ERROR_RATE_LIMIT or error_code == ERROR_SERVER
                ) and attempt < self.max_retries - 1

                if should_retry:
                    delay = self._get_delay(attempt)
                    logging.warning(
                        f"Error: {error_code}. Retrying in {delay:.2f} seconds... (Attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                else:
                    # For non-rate limit errors or the last attempt, return an error message
                    if attempt == self.max_retries - 1:
                        error_code = ERROR_MAX_RETRIES
                    return f"{ERROR_PREFIX}: {error_code} - {str(e)}", 0

    def chat_streamly(self, system, history, gen_conf):
        if system:
            if not gen_conf.get("enable_cot"):
                system = system + "/no_think"
            else:
                system = system + "/think"
            history.insert(0, {"role": "system", "content": system})
        if "max_tokens" in gen_conf:
            del gen_conf["max_tokens"]
        ans = ""
        reasoning = ""
        total_tokens = 0

        # F8080 思维链输出开关处理
        extra_body = {}
        if "enable_cot" in gen_conf:
            if not gen_conf.get("enable_cot"):
                extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
            gen_conf.pop("enable_cot")
        else:
            extra_body = {"chat_template_kwargs": {"enable_thinking": False}}

        if "internet" in gen_conf:
            gen_conf.pop("internet")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=history,
                stream=True,
                extra_body=extra_body,
                **gen_conf,
            )

            has_reasoning = False
            for resp in response:
                if not resp.choices:
                    continue

                # F8080 加入思维链内容提取
                reasoning = getattr(
                    getattr(getattr(resp, "choices", [{}])[0], "delta", {}),
                    "reasoning_content",
                    "",
                )
                if reasoning is not None and reasoning != "":
                    has_reasoning = True
                    if "<think>" not in ans:
                        ans += "<think>"
                    ans += reasoning

                content = getattr(
                    getattr(getattr(resp, "choices", [{}])[0], "delta", {}),
                    "content",
                    "",
                )
                if content is not None and content != "":
                    if "<think>" in ans and "</think>" not in ans and has_reasoning:
                        ans += "</think>"
                    ans += content

                tol = self.total_token_count(resp)
                if not tol:
                    total_tokens += len(resp.choices[0].delta.content)
                else:
                    total_tokens = tol

                yield ans

        except openai.APIError as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens

    def total_token_count(self, resp):
        try:
            return resp.usage.total_tokens
        except Exception:
            pass
        try:
            return resp["usage"]["total_tokens"]
        except Exception:
            pass
        return 0


class OpenAI_APIChat(Base):
    def __init__(self, key, model_name, base_url):
        if not base_url:
            raise ValueError("url cannot be None")
        model_name = model_name.split("___")[0]
        super().__init__(key, model_name, base_url)


class UniinChat(Base):
    """F8080 - 模型聚合平台接口

    Args:
        Base (_type_): _description_
    """

    def __init__(self, key, model_name, base_url="https://openai.uniin.cn/openapi/v1"):
        if not base_url:
            base_url = "https://openai.uniin.cn/openapi/v1"
        super().__init__(key, model_name, base_url)

    def chat(self, system, history, gen_conf):
        if "qwen3" in self.model_name.lower() or "qwq" in self.model_name.lower():
            return self.chat_using_stream(system, history, gen_conf)

        exp_seconds = 3600000

        if system:
            history.insert(0, {"role": "system", "content": system})
        # if "max_tokens" in gen_conf:
        #     del gen_conf["max_tokens"]

        clear_gen_conf(gen_conf)
        try:
            response = ""
            response = cniin_llm.completions(
                os.environ.get("UNIIN_APP_KEY"),
                os.environ.get("UNIIN_APP_SECRET"),
                exp_seconds,
                self.model_name,
                history,
                **gen_conf,
            )

            ans = ""
            has_reasoning = False
            # resp_str = response.decode('utf-8').replace('data:', '')
            resp = json.loads(response).get("data")

            if (
                not resp.get("choices")
                or not isinstance(resp.get("choices"), list)
                or len(resp.get("choices")) <= 0
            ):
                return ans, 0

            reasoning = (
                resp.get("choices", [{}])[0]
                .get("message", {})
                .get("reasoning_content", None)
            )
            if reasoning is not None and reasoning != "":
                has_reasoning = True
                if "<think>" not in ans:
                    ans += "<think>"
                ans += reasoning

            content = (
                resp.get("choices", [{}])[0].get("message", {}).get("content", None)
            )
            if content is not None and content != "":
                if "<think>" in ans and "</think>" not in ans and has_reasoning:
                    ans += "</think>"
                ans += content

            return ans, self.total_token_count(ans)

        except Exception as e:
            return response + "\n**ERROR**: " + str(e), 0

    def chat_using_stream(self, system, history, gen_conf):
        """用流式方法调用，但是一次性返回回答

        Args:
            system (_type_): _description_
            history (_type_): _description_
            gen_conf (_type_): _description_

        Yields:
            _type_: _description_
        """
        exp_seconds = 3600000

        last_msg = history[-1]
        last_msg_content = last_msg["content"]
        if "qwen3" in self.model_name.lower() or "qwq" in self.model_name.lower():
            if gen_conf.get("enable_cot", False):
                last_msg["content"] = last_msg["content"] + "/think"
            else:
                last_msg["content"] = last_msg["content"] + "/no_think"

        if system:
            history.insert(0, {"role": "system", "content": system})

        ans = ""
        reasoning = ""

        try:
            response = cniin_llm.stream_completions(
                os.environ.get("UNIIN_APP_KEY"),
                os.environ.get("UNIIN_APP_SECRET"),
                exp_seconds,
                self.model_name,
                history,
                **gen_conf,
            )
            last_msg["content"] = last_msg_content

            has_reasoning = False
            for chunk in response.iter_lines():
                if not chunk:
                    continue

                resp_str = chunk.decode("utf-8").replace("data:", "")
                resp = json.loads(resp_str).get("data")

                if (
                    not resp.get("choices")
                    or not isinstance(resp.get("choices"), list)
                    or len(resp.get("choices")) <= 0
                ):
                    continue

                reasoning = (
                    resp.get("choices", [{}])[0]
                    .get("message", {})
                    .get("reasoning_content", None)
                )
                if reasoning is not None and reasoning != "":
                    has_reasoning = True
                    if "<think>" not in ans:
                        ans += "<think>"
                    ans += reasoning

                content = (
                    resp.get("choices", [{}])[0].get("message", {}).get("content", None)
                )
                if content is not None and content != "":
                    if "<think>" in ans and "</think>" not in ans and has_reasoning:
                        ans += "</think>"
                    ans += content

        except Exception as e:
            ans = ans + "\n**ERROR**: " + str(e)

        return ans, self.total_token_count(ans)

    def chat_streamly(self, system, history, gen_conf):
        exp_seconds = 3600000

        last_msg = history[-1]
        last_msg_content = last_msg["content"]
        if "qwen3" in self.model_name.lower() or "qwq" in self.model_name.lower():
            if gen_conf.get("enable_cot", False):
                last_msg["content"] = last_msg["content"] + "/think"
            else:
                last_msg["content"] = last_msg["content"] + "/no_think"

        history.insert(0, {"role": "system", "content": system})
        ans = ""
        reasoning = ""
        total_tokens = 0
        clear_gen_conf(gen_conf)
        try:
            response = cniin_llm.stream_completions(
                os.environ.get("UNIIN_APP_KEY"),
                os.environ.get("UNIIN_APP_SECRET"),
                exp_seconds,
                self.model_name,
                history,
                **gen_conf,
            )
            last_msg["content"] = last_msg_content

            has_reasoning = False
            for chunk in response.iter_lines():
                if not chunk:
                    continue

                resp_str = chunk.decode("utf-8").replace("data:", "")
                resp = json.loads(resp_str).get("data")

                if (
                    not resp.get("choices")
                    or not isinstance(resp.get("choices"), list)
                    or len(resp.get("choices")) <= 0
                ):
                    continue

                reasoning = (
                    resp.get("choices", [{}])[0]
                    .get("message", {})
                    .get("reasoning_content", None)
                )
                if reasoning is not None and reasoning != "":
                    has_reasoning = True
                    if "<think>" not in ans:
                        ans += "<think>"
                    ans += reasoning

                content = (
                    resp.get("choices", [{}])[0].get("message", {}).get("content", None)
                )
                if content is not None and content != "":
                    if "<think>" in ans and "</think>" not in ans and has_reasoning:
                        ans += "</think>"
                    ans += content

                total_tokens = len(ans)
                yield ans

        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield total_tokens


def split_model_name_and_factory(model_name):
    arr = model_name.split("@")
    if len(arr) < 2:
        return model_name, None
    return arr[0], arr[1]


def get_chat_mdl(llm_id):
    llm_id, model_provider = split_model_name_and_factory(llm_id)
    if "Uniin" in model_provider:
        return UniinChat("", llm_id)

    if "OpenAI-API" in model_provider:
        return OpenAI_APIChat(
            os.environ.get("OPENAI_API_KEY"),
            llm_id,
            os.environ.get("OPENAI_API_BASE_URL"),
        )
