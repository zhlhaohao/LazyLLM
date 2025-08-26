import os
import argparse
from fastmcp.server import FastMCP
from mcps.servers.general.general import intent_classifier

def create_server():
    mcp_server = FastMCP("General MCP Tools")
    mcp_server.tool()(intent_classifier)
    return mcp_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port if args.port else int(os.environ.get("PORT"))

    create_server().run(
        transport="streamable-http", host="0.0.0.0", port=port, path="/mcp-server"
    )