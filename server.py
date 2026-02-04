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
    try:
        tools = await mcp.list_tools()
        # Serialize the tools list to JSON compatible format
        tools_data = []
        for tool in tools:
            try:
                tool_dict = tool.model_dump()
                tools_data.append(tool_dict)
            except Exception as e:
                logger.error(f"Error serializing tool: {e}")
                # Add a fallback tool representation
                tools_data.append({"name": "error", "description": f"Error serializing tool: {e}"})
        
        return JSONResponse(tools_data)
    except Exception as e:
        logger.error(f"Error in handle_tools: {e}")
        try:
            return JSONResponse({"error": str(e)}, status_code=500)
        except Exception as inner_e:
            logger.error(f"Error creating error response: {inner_e}")
            # Return a simple text response as a last resort
            from starlette.responses import PlainTextResponse
            return PlainTextResponse(f"Error: {str(e)}", status_code=500)

# 创建 Starlette 应用
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        try:
            async def send(message):
                await request._send(message)
            
            async with sse.connect_sse(
                    request.scope,
                    request.receive,
                    send,
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            # SSE handler shouldn't return a response, but ensure we don't return None
            # Return a 204 No Content response as SSE connections are long-lived
            from starlette.responses import Response
            return Response(status_code=204)
        except Exception as e:
            logger.error(f"Error in handle_sse: {e}")
            # Return an error response if an exception occurs
            from starlette.responses import PlainTextResponse
            return PlainTextResponse(f"Error: {str(e)}", status_code=500)

    # 包装sse.handle_post_message以添加错误处理
    original_handle_post_message = sse.handle_post_message
    
    async def wrapped_handle_post_message(scope, receive, send):
        try:
            await original_handle_post_message(scope, receive, send)
        except Exception as e:
            logger.error(f"Error in wrapped_handle_post_message: {e}")
            # 尝试发送错误响应
            try:
                error_message = f"Error: {str(e)}"
                await send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [
                        (b"content-type", b"text/plain; charset=utf-8"),
                        (b"content-length", str(len(error_message)).encode()),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": error_message.encode(),
                })
            except Exception as inner_e:
                logger.error(f"Error sending error response: {inner_e}")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=wrapped_handle_post_message),
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
    
    uvicorn.run(starlette_app, host=args.host, port=args.port, workers=1)
