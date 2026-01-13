from typing import Any
import argparse
import logging
import uvicorn
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
from mcp.server import Server

# Import the configured FastMCP instance from skills
from skills.sim_tools import mcp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sim-mcp-server")

async def handle_tools(request: Request):
    """
    Handle /mcp/tools endpoint.
    Returns the list of tools available on this MCP server.
    """
    tools = await mcp.list_tools()
    # Serialize the tools list to JSON compatible format
    tools_data = [tool.model_dump() for tool in tools]
    return JSONResponse(tools_data)

# 创建 Starlette 应用
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/mcp/tools", endpoint=handle_tools, methods=["GET"]),
        ],
    )

if __name__ == "__main__":
    # Access the underlying low-level Server object from FastMCP
    mcp_server = mcp._mcp_server

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=80, help='Port to listen on')
    args = parser.parse_args()

    # 创建并运行 Starlette 应用
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    print(f"Starting SSE server on http://{args.host}:{args.port}")
    print(f"Tools available at http://{args.host}:{args.port}/mcp/tools")
    
    uvicorn.run(starlette_app, host=args.host, port=args.port)
