import os
import argparse
from fastmcp.server import FastMCP
from mcps.servers.web_research.research import web_research

def create_server():
    mcp_server = FastMCP("LazyLLM MCP Server")
    mcp_server.tool()(web_research)
    return mcp_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port if args.port else int(os.environ.get("PORT"))

    create_server().run(
        transport="streamable-http", host="0.0.0.0", port=port, path="/mcp-server"
    )