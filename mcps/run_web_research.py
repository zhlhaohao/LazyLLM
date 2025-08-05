import os
from fastmcp.server import FastMCP
from mcps.servers.web_research.research import web_research

def create_server():
    mcp_server = FastMCP("LazyLLM MCP Server")
    mcp_server.tool()(web_research)
    return mcp_server


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10001))
    create_server().run(
        transport="streamable-http", host="0.0.0.0", port=port, path="/mcp-server"
    )
