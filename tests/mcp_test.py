import asyncio
from mcps.client.mcp_chat import McpChat


async def main() -> None:
    """Initialize and run the chat session."""
    print("start mcp chat...")
    mcp_chat = McpChat()
    await mcp_chat.init_servers()
    mcp_chat.mcp_instruction(["TestServer"])
    server = mcp_chat.get_server("TestServer")

    result = await server.execute_tool(
        "web_research",
        {
            "query": "请分析芬太尼的化学结构，与吗啡 杜冷丁进行比较",
            # "query": "今天广州天气如何",
        },
    )

    # print(f"tool result:{result}")


if __name__ == "__main__":
    asyncio.run(main())
