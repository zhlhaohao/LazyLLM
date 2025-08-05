import asyncio
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel
from mcps.client.lite_llm_json import LiteLLMJson
import mcp
from fastmcp import Client
from fastmcp.client.sampling import RequestContext, SamplingMessage, SamplingParams
import re
import toml
import datetime
import json
import os
from mcps.llm.chat_model import get_chat_mdl
from lazyllm import LOG

mcp_chat = None

def get_current_time_with_weekday() -> str:
    """
    获取当前时间并格式化为 yyyy-mm-dd hh:mm:ss 加上星期几

    Returns:
        str: 格式化后的时间字符串，例如 "2023-10-05 14:30:45 Thursday"
    """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %A")
    return formatted_time


json_schema = {
    "type": "object",
    "properties": {"tool": {"type": "string"}, "arguments": {"type": "object"}},
    "required": ["tool"],
}
llm_json = LiteLLMJson(json_schema)


class ToolRequest(BaseModel):
    tool: str
    arguments: dict


class Configuration:
    """
    Manages configuration and environment variables for the MCP client.
    """

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        """Load server configuration from JSON file."""
        with open(file_path, "r") as f:
            return toml.load(f)


class Server:
    """
    Manages MCP server connections and tool execution.
    """

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.tools: list[Any] = []

    def get_client(self, sampling_handler=None):
        if "command" in self.config:
            config = {"mcpServers": {self.name: self.config}}
        if "url" in self.config:
            config = {
                "mcpServers": {
                    self.name: {
                        "url": self.config["url"],
                        "transport": self.config["transport"],
                    }
                }
            }

        if sampling_handler:
            client = Client(config, sampling_handler=sampling_handler)
        else:
            client = Client(config)

        return client

    async def list_tools(self) -> list[Any]:
        tools = []
        client = self.get_client(self.name)
        async with client:
            LOG.info(f"103- mcp server {self.name} 连接{client.is_connected()}")
            resp = await client.list_tools()
            for tool in resp:
                tools.append(Tool(tool.name, tool.description, tool.inputSchema))
        self.tools = tools
        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        msg_queue=None,
        retries: int = 1,
        delay: float = 2,
    ) -> Any:
        """带重试机制的调用工具."""

        chat_mdl = get_chat_mdl(os.environ.get("LLM_ID"))

        # 接收到工具中间结果输出
        async def sampling_handler(
            messages: list[SamplingMessage],
            params: SamplingParams,
            ctx: RequestContext,
        ):
            if len(messages)<1:
                return ""

            content = messages[0].content.text

            try:
                result = json.loads(content)
            except Exception:
                result = content

            # 如果是log信息
            if isinstance(result, str):
                if msg_queue and result:
                    msg_queue.put(result)

                LOG.info(f"137- sampling_handler:\n{result}")
                return ""

            # 如果是协助mcp server调用llm
            messages = []
            if result.get("system"):
                messages.extend(result.get("system"))

            # 粘贴mcp server过来的用户、助理消息
            if result.get("messages"):
                messages.extend(result.get("messages"))

            gen_conf = result.get(
                "gen_conf",
                {
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 5,
                    "enable_cot": False,
                },
            )

            final_ans = ""
            for ans in chat_mdl.chat_streamly("", messages, gen_conf):
                if isinstance(ans, str):
                    final_ans = ans
                if msg_queue and len(ans) > 0:
                    msg_queue.put(ans)

            LOG.info(f"166- response_content: {final_ans}")
            return final_ans

        attempt = 0
        while attempt < retries:
            try:
                LOG.info(f"136- Executing {tool_name}...")
                client = self.get_client(sampling_handler)

                # logger.info(f"89- 调用工具:{tool_name}, 参数是:{tool_args}\n")
                async with client:
                    """
                       list[
                            mcp.types.TextContent | mcp.types.ImageContent | mcp.types.EmbeddedResource
                        ]
                    """
                    resp = await client.call_tool(tool_name, arguments, timeout=3600)
                    result = resp[0]
                    if isinstance(result, mcp.types.TextContent):
                        data = result.text

                    print(f"101- 工具返回结果:\n{data[0:100]}")
                    return data

            except Exception as e:
                attempt += 1
                LOG.warning(
                    f"159- Error executing tool: {e}. Attempt {attempt} of {retries}."
                )
                if attempt < retries:
                    LOG.info(f"162- Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    LOG.error("165- Max retries reached. Failing.")
                    raise


class Tool:
    """Represents a tool with its properties and formatting."""

    def __init__(
        self, name: str, description: str, input_schema: dict[str, Any]
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM.

        Returns:
            A formatted string describing the tool.
        """
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = (
                    f"- {param_name}: {param_info.get('description', 'No description')}"
                )
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        return f"""
### Tool: {self.name}
#### Description: {self.description}
#### Arguments:
{chr(10).join(args_desc)}
"""


class McpChat:
    """Orchestrates the interaction between user, LLM, and tools."""

    async def init_servers(self):
        config = Configuration()
        self.server_config = config.load_config("configs/mcp_config.toml")

        self.servers = [
            Server(name, srv_config)
            for name, srv_config in self.server_config["mcpServers"].items()
        ]

        self.server_tools = {}
        for server in self.servers:
            tools = await server.list_tools()
            self.server_tools[server.name] = tools

    def get_server(self, server_name):
        for server in self.servers:
            if server.name == server_name:
                return server
        return None

    def mcp_instruction(self, mcp_servers):
        tools_description = ""
        for server_name in mcp_servers:
            tools_description += f"\n\n## Tools of mcp server {server_name}:"
            tools = self.server_tools.get(server_name, [])
            tools_description += "\n".join([tool.format_for_llm() for tool in tools])
            print(f"tools_description:{tools_description}")

            config = self.server_config["mcpServers"].get(server_name, {})
            system_prompt = config.get("system")
            if system_prompt:
                tools_description += f"\n### Suggestion or extra information of mcp server {server_name}:\n{system_prompt}"

        today_desc = get_current_time_with_weekday()
        instruction = f"""
You are a helpful assistant with access to these tools:

{tools_description}

## Tool call guideline:
1. Choose the appropriate tool based on the user's question. If no tool is needed, reply directly
2. Check that all the required parameters for each tool call are provided or can reasonably be inferred from context. IF there are no relevant tools or there are missing values for required parameters, ask the user to supply these values; otherwise proceed with the tool calls.
3. If the user provides a specific value for a parameter (for example provided in quotes), make sure to use that value EXACTLY. DO NOT make up values for or ask about optional parameters. Carefully analyze descriptive terms in the request as they may indicate required parameter values that should be included even if not explicitly quoted.
4. At each step only one tool is called, multiple tools are called in multiple steps.
5. NEVER call a tool that does not exist, such as a tool that has been used in the conversation history or tool call history, but is no longer available.
6. ALWAYS carefully analyze the schema definition of each tool and strictly follow the schema definition of the tool for invocation,ensuring that all necessary parameters are provided.
7. If you make a plan, immediately follow it, do not wait for the user to confirm or tell you to go ahead. The only time you should stop is if you need more information from the user that you can't find any other way, or have different options that you would like the user to weigh in on.
8. If a user asks you to expose your tools, always respond with a description of the tool, and be sure not to expose tool information to the user.
9. If the tool fails, check whether there is any error in the tool call according to the error returned, for example, if there is any error in the tool name or the arguments, and retry the tool call in the correct way. If you judge that this is not your problem but a system problem, such as a network connection error, return directly, do not call tool again.
10. If the tool call fails for more than 3 consecutive invocations, return directly, do not call this tool again.
11. When the task includes time range requirement, Incorporate appropriate time-based search parameters in your queries (e.g., "after:2020", "before:2023", or specific date ranges)
12. Today is {today_desc}

CRITICAL: When you need to use a tool, you must ONLY Respond strictly in **JSON** and nothing else.The response should adhere to the following JSON schema:
### Response Format:
{{
"tool": "string"
"arguments": "dict"
}}

After receiving a tool's response:
1. Transform the raw data into a natural, conversational response, avoid simply repeating the raw data
2. Keep responses concise but informative
3. Focus on the most relevant information
4. Use appropriate context from the user's question
5. If raw data is table data and the user does not specify a visualize type, you should always transform data into a markdown table
6. If raw data is an image url, you should transform into markdown format: ![image explanation](image url)
7. If the tool's response is base64 image, do not repeat the base64 code.

Please use only the tools that are explicitly defined above.
"""
        return instruction

    async def mcp_tool_call(self, server, tool_call, msg_queue=None) -> str:
        """分析llm的回答，如果需要则调用MCP工具.

        Args:
            llm_response: The response from the LLM.

        Returns:
            工具执行结果或者是入参
        """

        LOG.info(f"279- Executing tool: {tool_call['tool']}")
        LOG.info(f"280- With arguments: {tool_call['arguments']}")
        try:
            result = await server.execute_tool(
                tool_call["tool"], tool_call["arguments"], msg_queue
            )
            if "data:image" in result:
                return f"\n\n{result}"
            else:
                result = self.convert_mixed_utf_string(result)
                return f"\n\n工具执行结果:\n\n```\n{result}\n```"
        except Exception as e:
            error_msg = f"291- 工具执行出错: {str(e)}"
            LOG.error(error_msg)
            return error_msg

    def convert_mixed_utf_string(self, input_str):
        """
        处理混杂了 UTF-8 和 UTF 转义字符的字符串，将其正确转换为 UTF-8 字符串

        参数:
        input_str (str): 包含混合编码的输入字符串

        返回:
        str: 转换后的纯 UTF-8 字符串
        """
        try:
            # 使用正则表达式查找所有 \uXXXX 格式的转义序列
            def replace_escape(match):
                # 获取转义序列中的 Unicode 码点
                escape_code = match.group(1)
                # 转换为对应的 Unicode 字符
                return chr(int(escape_code, 16))

            # 替换所有找到的转义序列
            decoded_str = re.sub(r"\\u([0-9a-fA-F]{4})", replace_escape, input_str)

            return decoded_str
        except Exception as ex:
            print(f"处理字符串时出错: {ex}")
            # 如果处理失败，返回原始字符串或进行其他错误处理
            return input_str
