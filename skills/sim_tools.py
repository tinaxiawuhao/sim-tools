from mcp.server.fastmcp import FastMCP
from .sim_client import SimClient
import functools
from typing import Optional, Any

# Create the FastMCP server instance
mcp = FastMCP[Any]("sim-mcp-sse")

def ensure_login(func):
    """Decorator to check if user is logged in before executing the tool."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Allow login tool to pass through
        if func.__name__ == "login":
            return await func(*args, **kwargs)
        
        if not SimClient.is_logged_in():
            return "Error: You must login first using the 'login' tool."
        
        return await func(*args, **kwargs)
    return wrapper

@mcp.tool()
async def login(username: str, password: str) -> str:
    """
    登录仿真平台获取 Access Token。
    必须在调用其他工具前先调用此工具。

    Args:
    username: 账户 (必填)
    password: 密码 (必填)
    """
    return await SimClient.login(username, password)


@mcp.tool()
@ensure_login
async def get_user_list(company_id: int, login_name: Optional[str] = None) -> str:
    """
    获取组织列表
    
    Args:
        company_id: 公司ID (必填)
    """
    params = {"companyId": company_id}
        
    result = await SimClient.get("/api/company/getCompanyInfoList", params=params)
    return str(result)


@mcp.tool()
async def check_login_status() -> str:
    """
    检查当前登录状态。
    """
    is_logged_in = SimClient.is_logged_in()
    return f"Login status: {is_logged_in}"
