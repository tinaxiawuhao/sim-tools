from mcp.server.fastmcp import FastMCP
from .sim_client import SimClient
import functools
from typing import Optional, List, Dict, Any

# Create the FastMCP server instance
mcp = FastMCP("sim-mcp-sse")

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
    Login to the simulation platform to obtain an access token.
    Must be called before any other tools.
    """
    return await SimClient.login(username, password)

@mcp.tool()
@ensure_login
async def query_cases_list(
    case_name: Optional[str] = None,
    page_index: int = 1,
    page_size: int = 10
) -> str:
    """
    Query the list of simulation cases.
    
    Args:
        case_name: Filter by case name (optional)
        page_index: Page number (default 1)
        page_size: Page size (default 10)
    """
    payload = {
        "pageIndex": page_index,
        "pageSize": page_size
    }
    if case_name:
        payload["caseName"] = case_name
        
    result = await SimClient.post("/api/case/queryCasesList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_user_list(login_name: Optional[str] = None) -> str:
    """
    Get a list of users.
    
    Args:
        login_name: Filter by login name (optional)
    """
    params = {}
    if login_name:
        params["loginName"] = login_name
        
    result = await SimClient.get("/api/user/getUserList", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_templates(
    template_name: Optional[str] = None,
    case_id: Optional[int] = None
) -> str:
    """
    Query value stream templates by conditions.
    """
    payload = {}
    if template_name:
        payload["templateName"] = template_name
    if case_id:
        payload["caseId"] = case_id
        
    result = await SimClient.post("/api/valueStreamTemplate/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_case_details(case_id: int) -> str:
    """
    Query case details by case ID.
    """
    result = await SimClient.get("/api/case/queryCaseDetails", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def delete_case(case_id: int) -> str:
    """
    Delete a case by case ID.
    """
    result = await SimClient.delete("/api/case/deleteCase", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_model_point(
    case_id: str,
    index_code: str,
    point_name: str,
    bind_point_name: str,
    point_type: int,
    id: Optional[int] = None,
    model_code: Optional[str] = None,
    production_material_code: Optional[str] = None,
    point_desc: Optional[str] = None,
    default_value: Optional[str] = None,
    point_length: Optional[str] = None,
    sort: Optional[int] = None
) -> str:
    """
    Save or update a case model point (local PLC debugging).
    
    Args:
        case_id: Case ID (required)
        index_code: Model instance index code (required)
        point_name: Axis point name (required)
        bind_point_name: Bound IoT point name (required)
        point_type: Point type (1: Input, 2: Output) (required)
        id: Primary key (optional, for update)
        model_code: Model code (optional)
        production_material_code: Production material code (optional)
        point_desc: Field description (optional)
        default_value: Default value (optional)
        point_length: Field length (optional)
        sort: Sort order (optional)
    """
    payload = {
        "caseId": case_id,
        "indexCode": index_code,
        "pointName": point_name,
        "bindPointName": bind_point_name,
        "pointType": point_type
    }
    
    if id is not None: payload["id"] = id
    if model_code: payload["modelCode"] = model_code
    if production_material_code: payload["productionMaterialCode"] = production_material_code
    if point_desc: payload["pointDesc"] = point_desc
    if default_value: payload["defaultValue"] = default_value
    if point_length: payload["pointLength"] = point_length
    if sort is not None: payload["sort"] = sort
    
    result = await SimClient.post("/api/caseModelPointLocal/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_case_model_points(
    case_id: str,
    index_code: Optional[str] = None,
    model_code: Optional[str] = None
) -> str:
    """
    Query case model points by conditions.
    
    Args:
        case_id: Case ID (required)
        index_code: Model instance index code (optional)
        model_code: Model code (optional)
    """
    payload = {"caseId": case_id}
    if index_code: payload["indexCode"] = index_code
    if model_code: payload["modelCode"] = model_code
    
    result = await SimClient.post("/api/caseModelPointLocal/queryByList", data=payload)
    return str(result)
