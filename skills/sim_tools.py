from mcp.server.fastmcp import FastMCP
from .sim_client import SimClient
import functools
from typing import Optional, List, Dict, Any

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
    """
    return await SimClient.login(username, password)

@mcp.tool()
@ensure_login
async def query_cases_list(
    case_name: Optional[str] = None,
    publish_state: Optional[int] = None
) -> str:
    """
    查询仿真案例列表。
    
    Args:
        case_name: 案例名称过滤 (可选)
        publish_state: 发布状态过滤 (可选)
    """
    params = {}
    if case_name:
        params["keyWord"] = case_name
    if publish_state is not None:
        params["publishState"] = publish_state
        
    result = await SimClient.get("/api/case/queryCasesList", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def get_user_list(company_id: int, login_name: Optional[str] = None) -> str:
    """
    获取用户列表。
    
    Args:
        company_id: 公司ID (必填)
        login_name: 登录名过滤 (可选)
    """
    params = {"companyId": company_id}
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
    根据条件查询价值流模板列表。
    
    Args:
        template_name: 模板名称 (可选)
        case_id: 案例ID (可选)
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
    根据案例ID查询案例明细。
    """
    result = await SimClient.get("/api/case/queryCaseDetails", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def delete_case(case_id: int) -> str:
    """
    根据案例ID删除案例。
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
    保存或更新案例模型点位 (Local PLC Debugging)。
    
    Args:
        case_id: 案例ID (必填)
        index_code: 模型实例索引代码 (必填)
        point_name: 轴点位名称 (必填)
        bind_point_name: 绑定IoT点位名称 (必填)
        point_type: 点位类型 (1: Input, 2: Output) (必填)
        id: 主键 (可选，更新时必填)
        model_code: 模型代码 (可选)
        production_material_code: 生产物料代码 (可选)
        point_desc: 字段描述 (可选)
        default_value: 默认值 (可选)
        point_length: 字段长度 (可选)
        sort: 排序 (可选)
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
    根据条件查询案例模型点位。
    
    Args:
        case_id: 案例ID (必填)
        index_code: 模型实例索引代码 (可选)
        model_code: 模型代码 (可选)
    """
    payload = {"caseId": case_id}
    if index_code: payload["indexCode"] = index_code
    if model_code: payload["modelCode"] = model_code
    
    result = await SimClient.post("/api/caseModelPointLocal/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_value_stream_template(
    template_name: str,
    template_json: str,
    id: Optional[int] = None,
    case_id: Optional[int] = None
) -> str:
    """
    新增或编辑价值流模板。
    
    Args:
        template_name: 模板名称 (必填)
        template_json: 模板JSON内容 (必填)
        id: 模板ID (可选，更新时必填)
        case_id: 案例ID (可选)
    """
    payload = {
        "templateName": template_name,
        "templateJson": template_json
    }
    if id is not None: payload["id"] = id
    if case_id is not None: payload["caseId"] = case_id
    
    result = await SimClient.post("/api/valueStreamTemplate/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_value_stream_template(id: int) -> str:
    """
    根据主键删除价值流模板。
    """
    result = await SimClient.delete("/api/valueStreamTemplate/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_value_stream_object_data_box_list(
    case_id: Optional[int] = None,
    object_type: Optional[str] = None,
    object_name: Optional[str] = None
) -> str:
    """
    根据条件查询价值流对象数据框。
    
    Args:
        case_id: 案例ID (可选)
        object_type: 对象类型 (可选)
        object_name: 对象名称 (可选)
    """
    payload = {}
    if case_id is not None: payload["caseId"] = case_id
    if object_type: payload["objectType"] = object_type
    if object_name: payload["objectName"] = object_name
    
    result = await SimClient.post("/api/valueStreamObjectDataBox/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_value_stream_object_data_box(
    object_type: str,
    object_name: str,
    box_name: str,
    id: Optional[int] = None,
    case_id: Optional[int] = None,
    data_type: Optional[str] = None,
    box_data: Optional[str] = None
) -> str:
    """
    新增或编辑价值流对象数据框。
    
    Args:
        object_type: 对象类型 (必填)
        object_name: 对象名称 (必填)
        box_name: 数据框名称 (必填)
        id: 主键 (可选，更新时必填)
        case_id: 案例ID (可选)
        data_type: 数据类型 (可选)
        box_data: 数据框内容 (可选)
    """
    payload = {
        "objectType": object_type,
        "objectName": object_name,
        "boxName": box_name
    }
    if id is not None: payload["id"] = id
    if case_id is not None: payload["caseId"] = case_id
    if data_type: payload["dataType"] = data_type
    if box_data: payload["boxData"] = box_data
    
    result = await SimClient.post("/api/valueStreamObjectDataBox/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_value_stream_object_data_box(id: int) -> str:
    """
    根据主键删除价值流对象数据框。
    """
    result = await SimClient.delete("/api/valueStreamObjectDataBox/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_role_list(
    role_name: Optional[str] = None,
    role_type: int = 1,
    page: int = 1,
    size: int = 10
) -> str:
    """
    获取角色列表。
    
    Args:
        role_name: 角色名称 (可选)
        role_type: 角色类型 (0:管理员, 1:租户角色, 默认1)
        page: 页码 (默认 1)
        size: 每页数量 (默认 10)
    """
    payload = {
        "page": page,
        "size": size,
        "roleType": role_type
    }
    if role_name: payload["roleName"] = role_name
    
    result = await SimClient.post("/api/role/getRoleList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_role_info(id: int) -> str:
    """
    获取角色详情。
    """
    result = await SimClient.get("/api/role/getRoleInfo", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def create_role(role_name: str, role_type: int = 1, remark: Optional[str] = None) -> str:
    """
    创建角色。
    
    Args:
        role_name: 角色名称
        role_type: 角色类型 (0:管理员, 1:租户角色)
        remark: 备注
    """
    payload = {
        "roleName": role_name,
        "roleType": role_type
    }
    if remark: payload["remark"] = remark
    result = await SimClient.post("/api/role/createRole", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def update_role(id: int, role_name: str, role_type: int = 1, remark: Optional[str] = None) -> str:
    """
    更新角色。
    """
    payload = {
        "id": id,
        "roleName": role_name,
        "roleType": role_type
    }
    if remark: payload["remark"] = remark
    result = await SimClient.post("/api/role/updateRole", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_role(id: int) -> str:
    """
    删除角色。
    """
    result = await SimClient.delete("/api/role/deleteRole", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_model_group(
    group_name: str,
    parent_id: int = 0,
    id: Optional[int] = None,
    sort: int = 0
) -> str:
    """
    新增或编辑模型分组。
    
    Args:
        group_name: 分组名称
        parent_id: 父级ID (默认0)
        id: 主键 (更新时必填)
        sort: 排序
    """
    payload = {
        "groupName": group_name,
        "parentId": parent_id,
        "sort": sort
    }
    if id is not None: payload["id"] = id
    result = await SimClient.post("/api/modelGroup/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_model_group_list(group_name: Optional[str] = None) -> str:
    """
    获取模型分组列表。
    """
    payload = {}
    if group_name: payload["groupName"] = group_name
    result = await SimClient.post("/api/modelGroup/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_model_group(id: int) -> str:
    """
    删除模型分组。
    """
    result = await SimClient.delete("/api/modelGroup/remove", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_worker_task(
    task_name: str,
    case_id: int,
    task_type: int,
    id: Optional[int] = None,
    task_desc: Optional[str] = None
) -> str:
    """
    新增或编辑工人任务。
    
    Args:
        task_name: 任务名称
        case_id: 案例ID
        task_type: 任务类型
        id: 任务ID (更新时必填)
        task_desc: 任务描述
    """
    payload = {
        "taskName": task_name,
        "caseId": case_id,
        "taskType": task_type
    }
    if id is not None: payload["id"] = id
    if task_desc: payload["taskDesc"] = task_desc
    
    result = await SimClient.post("/api/simWorkerTask/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_list(case_id: int) -> str:
    """
    查询工人任务列表。
    """
    payload = {"caseId": case_id}
    result = await SimClient.post("/api/simWorkerTask/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_worker_task(id: int) -> str:
    """
    删除工人任务。
    """
    result = await SimClient.delete("/api/simWorkerTask/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_value_stream_mapping(
    mapping_name: str,
    case_id: int,
    id: Optional[int] = None,
    mapping_json: Optional[str] = None
) -> str:
    """
    新增或编辑价值流映射。
    
    Args:
        mapping_name: 映射名称
        case_id: 案例ID
        id: 映射ID
        mapping_json: 映射JSON
    """
    payload = {
        "mappingName": mapping_name,
        "caseId": case_id
    }
    if id is not None: payload["id"] = id
    if mapping_json: payload["mappingJson"] = mapping_json
    
    result = await SimClient.post("/api/valueStreamMapping/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_value_stream_mapping_list(case_id: int) -> str:
    """
    查询价值流映射列表。
    """
    payload = {"caseId": case_id}
    result = await SimClient.post("/api/valueStreamMapping/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_value_stream_mapping(id: int) -> str:
    """
    删除价值流映射。
    """
    result = await SimClient.delete("/api/valueStreamMapping/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def create_user(
    username: str,
    login_name: str,
    role_ids: str,
    password: Optional[str] = None,
    mobile: Optional[str] = None
) -> str:
    """
    创建用户。
    
    Args:
        username: 用户名
        login_name: 登录名
        role_ids: 角色ID列表 (逗号分隔)
        password: 密码 (可选)
        mobile: 手机号 (可选)
    """
    payload = {
        "userName": username,
        "loginName": login_name,
        "roleIds": role_ids
    }
    if password: payload["password"] = password
    if mobile: payload["mobile"] = mobile
    
    result = await SimClient.post("/api/user/createUser", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def update_user(
    id: int,
    username: Optional[str] = None,
    mobile: Optional[str] = None,
    role_ids: Optional[str] = None
) -> str:
    """
    更新用户信息。
    """
    payload = {"id": id}
    if username: payload["userName"] = username
    if mobile: payload["mobile"] = mobile
    if role_ids: payload["roleIds"] = role_ids
    
    result = await SimClient.post("/api/user/updateUser", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_user(id: int) -> str:
    """
    删除用户。
    """
    result = await SimClient.delete("/api/user/deleteUser", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_current_user_info() -> str:
    """
    获取当前用户信息。
    """
    result = await SimClient.get("/api/user/getCurrentUserInfo")
    return str(result)

@mcp.tool()
@ensure_login
async def save_sys_style(
    style_name: str,
    style_code: str,
    id: Optional[int] = None,
    style_json: Optional[str] = None
) -> str:
    """
    保存系统样式。
    """
    payload = {
        "styleName": style_name,
        "styleCode": style_code
    }
    if id is not None: payload["id"] = id
    if style_json: payload["styleJson"] = style_json
    
    result = await SimClient.post("/api/sysStyle/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_sys_style_list(style_name: Optional[str] = None) -> str:
    """
    查询系统样式列表。
    """
    payload = {}
    if style_name: payload["styleName"] = style_name
    result = await SimClient.post("/api/sysStyle/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_sys_style(id: int) -> str:
    """
    删除系统样式。
    """
    result = await SimClient.delete("/api/sysStyle/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_layer_model(
    case_id: int,
    layer_name: str,
    id: Optional[int] = None,
    layer_json: Optional[str] = None
) -> str:
    """
    保存案例图层模型。
    """
    payload = {
        "caseId": case_id,
        "layerName": layer_name
    }
    if id is not None: payload["id"] = id
    if layer_json: payload["layerJson"] = layer_json
    
    result = await SimClient.post("/api/simCaseLayerModel/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_case_layer_list(case_id: int) -> str:
    """
    查询案例图层列表。
    """
    result = await SimClient.get("/api/simCaseLayerModel/queryLayerList", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_value_stream_object_base(
    object_name: str,
    object_type: str,
    id: Optional[int] = None,
    object_json: Optional[str] = None
) -> str:
    """
    保存价值流对象基础信息。
    """
    payload = {
        "objectName": object_name,
        "objectType": object_type
    }
    if id is not None: payload["id"] = id
    if object_json: payload["objectJson"] = object_json
    
    result = await SimClient.post("/api/valueStreamObjectBase/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_value_stream_object_base_list(object_name: Optional[str] = None) -> str:
    """
    查询价值流对象基础信息列表。
    """
    payload = {}
    if object_name: payload["objectName"] = object_name
    result = await SimClient.post("/api/valueStreamObjectBase/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_value_stream_object_base(id: int) -> str:
    """
    删除价值流对象基础信息。
    """
    result = await SimClient.delete("/api/valueStreamObjectBase/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_value_stream_object(
    object_name: str,
    case_id: int,
    object_type: str,
    id: Optional[int] = None,
    object_json: Optional[str] = None
) -> str:
    """
    保存价值流对象实例。
    """
    payload = {
        "objectName": object_name,
        "caseId": case_id,
        "objectType": object_type
    }
    if id is not None: payload["id"] = id
    if object_json: payload["objectJson"] = object_json
    
    result = await SimClient.post("/api/valueStreamObject/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_value_stream_object_list(case_id: int) -> str:
    """
    查询价值流对象实例列表。
    """
    payload = {"caseId": case_id}
    result = await SimClient.post("/api/valueStreamObject/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_value_stream_object(id: int) -> str:
    """
    删除价值流对象实例。
    """
    result = await SimClient.delete("/api/valueStreamObject/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_transport_detail(
    task_id: int,
    transport_name: str,
    id: Optional[int] = None
) -> str:
    """
    保存运输详情。
    """
    payload = {
        "taskId": task_id,
        "transportName": transport_name
    }
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/simWorkerTaskTransportDetail/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_transport_detail_list(task_id: int) -> str:
    """
    查询运输详情列表。
    """
    payload = {"taskId": task_id}
    result = await SimClient.post("/api/simWorkerTaskTransportDetail/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_transport_detail(id: int) -> str:
    """
    删除运输详情。
    """
    result = await SimClient.delete("/api/simWorkerTaskTransportDetail/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_machining_detail(
    task_id: int,
    machining_name: str,
    id: Optional[int] = None
) -> str:
    """
    保存加工详情。
    """
    payload = {
        "taskId": task_id,
        "machiningName": machining_name
    }
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/simWorkerTaskMachiningDetail/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_machining_detail_list(task_id: int) -> str:
    """
    查询加工详情列表。
    """
    payload = {"taskId": task_id}
    result = await SimClient.post("/api/simWorkerTaskMachiningDetail/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_machining_detail(id: int) -> str:
    """
    删除加工详情。
    """
    result = await SimClient.delete("/api/simWorkerTaskMachiningDetail/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def user_approval_pass_or_refuse(
    id: int,
    status: int,
    audit_opinion: Optional[str] = None
) -> str:
    """
    用户审批通过或拒绝。
    
    Args:
        id: 审批记录ID
        status: 状态 (1:通过, 2:拒绝)
        audit_opinion: 审批意见
    """
    payload = {
        "id": id,
        "status": status
    }
    if audit_opinion: payload["auditOpinion"] = audit_opinion
    
    result = await SimClient.post("/api/sysUserApproval/passOrRefuse", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_user_approval_list(
    page: int = 1,
    size: int = 10,
    status: Optional[int] = None
) -> str:
    """
    查询用户审批列表。
    """
    payload = {
        "page": page,
        "size": size
    }
    if status is not None: payload["status"] = status
    
    result = await SimClient.post("/api/sysUserApproval/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def create_user_approval(
    user_id: int,
    approval_type: int,
    approval_content: str
) -> str:
    """
    创建用户审批。
    """
    payload = {
        "userId": user_id,
        "approvalType": approval_type,
        "approvalContent": approval_content
    }
    result = await SimClient.post("/api/sysUserApproval/createUserApproval", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_company_list() -> str:
    """
    获取公司列表 (SysUserApproval)。
    """
    result = await SimClient.get("/api/sysUserApproval/getCompanyList")
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_layer(
    case_id: int,
    layer_name: str,
    layer_index: int,
    id: Optional[int] = None
) -> str:
    """
    保存案例图层。
    """
    payload = {
        "caseId": case_id,
        "layerName": layer_name,
        "layerIndex": layer_index
    }
    if id is not None: payload["id"] = id
    result = await SimClient.post("/api/simCaseLayerModel/saveLayer", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_case_layer(id: int) -> str:
    """
    查询案例图层详情。
    """
    result = await SimClient.get("/api/simCaseLayerModel/queryLayer", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_worksite_list(case_id: int) -> str:
    """
    查询工人任务-工位列表。
    """
    result = await SimClient.post("/api/simWorkerTask/queryWorksiteList", data={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_worker_list(case_id: int) -> str:
    """
    查询工人任务-工人列表。
    """
    result = await SimClient.post("/api/simWorkerTask/queryWorkerList", data={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_worker_group_list(case_id: int) -> str:
    """
    查询工人任务-工人分组列表。
    """
    result = await SimClient.post("/api/simWorkerTask/queryWorkerGroupList", data={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_material_list(case_id: int) -> str:
    """
    查询工人任务-物料列表。
    """
    result = await SimClient.post("/api/simWorkerTask/queryMaterialList", data={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_model_group_model_list(group_id: int) -> str:
    """
    获取模型分组下的模型列表。
    """
    result = await SimClient.get("/api/modelGroup/getModelList", params={"groupId": group_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_model_group_company_list() -> str:
    """
    获取模型分组公司列表。
    """
    result = await SimClient.get("/api/modelGroup/getCompanyList")
    return str(result)

@mcp.tool()
@ensure_login
async def copy_model_group(id: int) -> str:
    """
    复制模型分组。
    """
    result = await SimClient.post("/api/modelGroup/copy", data={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_model_group_by_id(id: int) -> str:
    """
    根据ID查询模型分组。
    """
    result = await SimClient.post("/api/modelGroup/queryById", data={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_model_group_model(
    group_id: int,
    model_id: int,
    id: Optional[int] = None
) -> str:
    """
    保存模型分组-模型关联。
    """
    payload = {
        "groupId": group_id,
        "modelId": model_id
    }
    if id is not None: payload["id"] = id
    result = await SimClient.post("/api/modelGroup/saveOrUpdateModel", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_object_by_id(id: int) -> str:
    """
    根据ID查询价值流对象实例。
    """
    result = await SimClient.get("/api/valueStreamObject/queryByOne", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_object_base_by_id(id: int) -> str:
    """
    根据ID查询价值流对象基础信息。
    """
    result = await SimClient.get("/api/valueStreamObjectBase/queryByOne", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_object_data_box_by_id(id: int) -> str:
    """
    根据ID查询价值流对象数据框。
    """
    result = await SimClient.get("/api/valueStreamObjectDataBox/queryByOne", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_mapping_by_id(id: int) -> str:
    """
    根据ID查询价值流映射。
    """
    result = await SimClient.get("/api/valueStreamMapping/queryByOne", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_stream_params(
    case_id: int,
    value_stream_base_id: int,
    object_type: str,
    source_type: int = 0
) -> str:
    """
    查询价值流对象参数。
    
    Args:
        case_id: 案例ID
        value_stream_base_id: 价值流组件ID
        object_type: 价值流对象标识
        source_type: 0:现状价值流，1:未来价值流
    """
    payload = {
        "caseId": case_id,
        "valueStreamBaseId": value_stream_base_id,
        "objectType": object_type,
        "sourceType": source_type
    }
    result = await SimClient.post("/api/valueStreamObjectBase/queryValueStreamParams", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_value_added_time(
    case_id: int,
    value_stream_base_id: int,
    object_type: str,
    source_type: int = 0
) -> str:
    """
    查询增值时间。
    
    Args:
        case_id: 案例ID
        value_stream_base_id: 价值流组件ID
        object_type: 价值流对象标识
        source_type: 0:现状价值流，1:未来价值流
    """
    payload = {
        "caseId": case_id,
        "valueStreamBaseId": value_stream_base_id,
        "objectType": object_type,
        "sourceType": source_type
    }
    result = await SimClient.post("/api/valueStreamObjectBase/queryValueAddedTime", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_process(case_id: int) -> str:
    """
    查询工序 (大纲视图)。
    
    Args:
        case_id: 案例ID
    """
    result = await SimClient.get("/api/valueStreamObjectBase/queryProcess", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_operation_flow(case_id: int) -> str:
    """
    查询操作流 (绑定业务流程)。
    
    Args:
        case_id: 案例ID
    """
    result = await SimClient.get("/api/valueStreamObjectDataBox/queryOperationFlow", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_data_type() -> str:
    """
    查询数据类型。
    """
    result = await SimClient.get("/api/valueStreamObjectDataBox/queryDataType")
    return str(result)

@mcp.tool()
@ensure_login
async def update_user_state(id: int, state: int) -> str:
    """
    更新用户状态。
    """
    result = await SimClient.post("/api/user/updateState", data={"id": id, "state": state})
    return str(result)

@mcp.tool()
@ensure_login
async def update_user_password(id: int, password: str) -> str:
    """
    更新用户密码。
    """
    result = await SimClient.post("/api/user/updatePassword", data={"id": id, "password": password})
    return str(result)

@mcp.tool()
@ensure_login
async def modify_role_data_access_permissions(role_id: int, permissions: str) -> str:
    """
    修改角色数据访问权限。
    """
    result = await SimClient.post("/api/role/modifyDataAccessPermissions", data={"roleId": role_id, "permissions": permissions})
    return str(result)

@mcp.tool()
@ensure_login
async def obtain_corresponding_permissions_for_roles(role_id: int) -> str:
    """
    获取角色对应的权限。
    """
    result = await SimClient.get("/api/role/obtainCorrespondingPermissionsForRoles", params={"roleId": role_id})
    return str(result)

@mcp.tool()
@ensure_login
async def batch_save_value_stream_template(json_list: str) -> str:
    """
    批量保存价值流模板 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.put("/api/valueStreamTemplate/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_delete_value_stream_template(ids: str) -> str:
    """
    批量删除价值流模板 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/valueStreamTemplate/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_value_stream_object_data_box(ids: str) -> str:
    """
    批量删除价值流对象数据框 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/valueStreamObjectDataBox/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_value_stream_object_base(ids: str) -> str:
    """
    批量删除价值流对象基础信息 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/valueStreamObjectBase/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_value_stream_object(ids: str) -> str:
    """
    批量删除价值流对象实例 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/valueStreamObject/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_value_stream_mapping(ids: str) -> str:
    """
    批量删除价值流映射 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/valueStreamMapping/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_user(ids: str) -> str:
    """
    批量删除用户 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.post("/api/user/batchDeleteUser", data={"ids": id_list})
    return str(result)

@mcp.tool()
@ensure_login
async def batch_pass_or_refuse_approval(ids: str, status: int, audit_opinion: Optional[str] = None) -> str:
    """
    批量通过或拒绝审批。
    """
    id_list = [int(x) for x in ids.split(",")]
    payload = {"ids": id_list, "status": status}
    if audit_opinion: payload["auditOpinion"] = audit_opinion
    result = await SimClient.post("/api/sysUserApproval/passOrRefuseBatch", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_sys_style(ids: str) -> str:
    """
    批量删除系统样式 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/sysStyle/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_transport_detail(ids: str) -> str:
    """
    批量删除运输详情 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/simWorkerTaskTransportDetail/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_machining_detail(ids: str) -> str:
    """
    批量删除加工详情 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/simWorkerTaskMachiningDetail/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_worker_task(ids: str) -> str:
    """
    批量删除工人任务 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/simWorkerTask/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_role(ids: str) -> str:
    """
    批量删除角色 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/role/batchDeleteRole", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_model_group(ids: str) -> str:
    """
    批量删除模型分组 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/modelGroup/removeByIds", data=id_list)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_save_value_stream_object_data_box(json_list: str) -> str:
    """
    批量保存价值流对象数据框 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/valueStreamObjectDataBox/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_value_stream_object_base(json_list: str) -> str:
    """
    批量保存价值流对象基础信息 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/valueStreamObjectBase/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_value_stream_object(json_list: str) -> str:
    """
    批量保存价值流对象实例 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/valueStreamObject/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_value_stream_mapping(json_list: str) -> str:
    """
    批量保存价值流映射 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/valueStreamMapping/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_sys_style(json_list: str) -> str:
    """
    批量保存系统样式 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/sysStyle/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_transport_detail(json_list: str) -> str:
    """
    批量保存运输详情 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/simWorkerTaskTransportDetail/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_machining_detail(json_list: str) -> str:
    """
    批量保存加工详情 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/simWorkerTaskMachiningDetail/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_worker_task(json_list: str) -> str:
    """
    批量保存工人任务 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/simWorkerTask/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_case_layer_model(json_list: str) -> str:
    """
    批量保存案例图层模型 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/simCaseLayerModel/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def batch_save_model_group(json_list: str) -> str:
    """
    批量保存模型分组 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/modelGroup/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def get_user_page(
    page: int = 1,
    size: int = 10,
    username: Optional[str] = None,
    login_name: Optional[str] = None
) -> str:
    """
    分页查询用户列表。
    """
    payload = {"page": page, "size": size}
    if username: payload["userName"] = username
    if login_name: payload["loginName"] = login_name
    result = await SimClient.post("/api/user/getUserPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_transport_detail_page(
    page: int = 1,
    size: int = 10,
    task_id: Optional[int] = None
) -> str:
    """
    分页查询运输详情。
    """
    payload = {"page": page, "size": size}
    if task_id is not None: payload["taskId"] = task_id
    result = await SimClient.post("/api/simWorkerTaskTransportDetail/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_machining_detail_page(
    page: int = 1,
    size: int = 10,
    task_id: Optional[int] = None
) -> str:
    """
    分页查询加工详情。
    """
    payload = {"page": page, "size": size}
    if task_id is not None: payload["taskId"] = task_id
    result = await SimClient.post("/api/simWorkerTaskMachiningDetail/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_task_page(
    page: int = 1,
    size: int = 10,
    case_id: Optional[int] = None,
    task_name: Optional[str] = None
) -> str:
    """
    分页查询工人任务。
    """
    payload = {"page": page, "size": size}
    if case_id is not None: payload["caseId"] = case_id
    if task_name: payload["taskName"] = task_name
    result = await SimClient.post("/api/simWorkerTask/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_role_page(
    page: int = 1,
    size: int = 10,
    role_name: Optional[str] = None,
    role_type: Optional[int] = None
) -> str:
    """
    分页查询角色列表。
    """
    payload = {"page": page, "size": size}
    if role_name: payload["roleName"] = role_name
    if role_type is not None: payload["roleType"] = role_type
    result = await SimClient.post("/api/role/getRolePage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_model_group_page(
    page: int = 1,
    size: int = 10,
    group_name: Optional[str] = None
) -> str:
    """
    分页查询模型分组。
    """
    payload = {"page": page, "size": size}
    if group_name: payload["groupName"] = group_name
    result = await SimClient.post("/api/modelGroup/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_user_info_by_id(id: int) -> str:
    """
    根据ID获取用户信息。
    """
    result = await SimClient.get("/api/user/getUserInfo", params={"id": id})
    return str(result)

# --- Case Management (Core) ---

@mcp.tool()
@ensure_login
async def save_case(
    case_name: str,
    case_type: int = 0,
    id: Optional[int] = None,
    remark: Optional[str] = None
) -> str:
    """
    保存或更新案例。
    
    Args:
        case_name: 案例名称
        case_type: 案例类型
        id: 案例ID (更新时必填)
        remark: 备注
    """
    payload = {
        "caseName": case_name,
        "caseType": case_type
    }
    if id is not None: payload["id"] = id
    if remark: payload["remark"] = remark
    result = await SimClient.post("/api/case/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def update_case_name(id: int, case_name: str) -> str:
    """
    更新案例名称。
    """
    result = await SimClient.post("/api/case/updateName", data={"id": id, "caseName": case_name})
    return str(result)

@mcp.tool()
@ensure_login
async def update_case_publish_state(id: int, state: int) -> str:
    """
    更新案例发布状态。
    """
    result = await SimClient.post("/api/case/updateCasePublishState", data={"id": id, "state": state})
    return str(result)

@mcp.tool()
@ensure_login
async def copy_case(id: int) -> str:
    """
    复制案例。
    """
    result = await SimClient.post("/api/case/caseCopy", data={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def batch_copy_case(ids: str) -> str:
    """
    批量复制案例 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.post("/api/case/caseBatchCopy", data={"ids": id_list})
    return str(result)

@mcp.tool()
@ensure_login
async def query_cases_by_page(
    page: int = 1,
    size: int = 10,
    case_name: Optional[str] = None,
    publish_state: Optional[int] = None,
    case_industry_json: Optional[str] = None,
    sim_type: Optional[int] = None
) -> str:
    """
    分页查询案例列表 (标准)。
    """
    params = {"page": page, "size": size}
    if case_name: params["keyWord"] = case_name
    if publish_state is not None: params["publishState"] = publish_state
    if case_industry_json: params["caseIndustryJson"] = case_industry_json
    if sim_type is not None: params["simType"] = sim_type
    result = await SimClient.get("/api/case/queryCasesByPage", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def query_cases_list_not_value_stream(
    page: int = 1,
    size: int = 10,
    case_name: Optional[str] = None,
    value_stream_type: Optional[int] = None
) -> str:
    """
    查询非价值流案例列表。
    """
    params = {"page": page, "size": size}
    if case_name: params["caseName"] = case_name
    if value_stream_type is not None: params["valueStreamType"] = value_stream_type
    result = await SimClient.get("/api/case/queryCasesListNotValueStream", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def query_cases_by_page_master_data(
    page: int = 1,
    size: int = 10,
    case_name: Optional[str] = None,
    publish_state: Optional[int] = None,
    case_industry_json: Optional[str] = None,
    sim_type: Optional[int] = None
) -> str:
    """
    分页查询案例列表 (主数据)。
    """
    params = {"page": page, "size": size}
    if case_name: params["keyWord"] = case_name
    if publish_state is not None: params["publishState"] = publish_state
    if case_industry_json: params["caseIndustryJson"] = case_industry_json
    if sim_type is not None: params["simType"] = sim_type
    result = await SimClient.get("/api/case/queryCasesByPageMasterData", params=params)
    return str(result)

# --- Case Model Point Local (Missing) ---

@mcp.tool()
@ensure_login
async def batch_save_case_model_point(json_list: str) -> str:
    """
    批量保存案例模型点位 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/caseModelPointLocal/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def delete_case_model_point(id: int) -> str:
    """
    删除案例模型点位。
    """
    result = await SimClient.delete("/api/caseModelPointLocal/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def batch_delete_case_model_point(ids: str) -> str:
    """
    批量删除案例模型点位 (ids逗号分隔)。
    """
    id_list = [int(x) for x in ids.split(",")]
    result = await SimClient.delete("/api/caseModelPointLocal/removeByIds", data=id_list)
    return str(result)

# --- Case Settings/Config ---

@mcp.tool()
@ensure_login
async def update_case_sim_type(id: int, sim_type: int) -> str:
    """
    更新案例仿真类型。
    """
    result = await SimClient.post("/api/case/updateCaseSimType", data={"id": id, "simType": sim_type})
    return str(result)

@mcp.tool()
@ensure_login
async def add_case_sim_type(id: int, sim_type: int) -> str:
    """
    添加案例仿真类型。
    """
    result = await SimClient.post("/api/case/addCaseSimType", data={"id": id, "simType": sim_type})
    return str(result)

@mcp.tool()
@ensure_login
async def update_outline_extends(id: int, outline_extends: str) -> str:
    """
    更新大纲扩展信息。
    """
    result = await SimClient.post("/api/case/updateOutlineExtends", data={"id": id, "outlineExtends": outline_extends})
    return str(result)

@mcp.tool()
@ensure_login
async def update_case_outline_views(id: int, outline_views: str) -> str:
    """
    更新案例大纲视图。
    """
    result = await SimClient.post("/api/case/updateCaseOutlineViews", data={"id": id, "outlineViews": outline_views})
    return str(result)

@mcp.tool()
@ensure_login
async def query_case_outline_views(id: int) -> str:
    """
    查询案例大纲视图。
    """
    result = await SimClient.get("/api/case/queryCaseOutlineViews", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_label(id: int, label: str) -> str:
    """
    保存案例标签。
    """
    result = await SimClient.post("/api/case/saveOrUpdateLabel", data={"id": id, "label": label})
    return str(result)

@mcp.tool()
@ensure_login
async def query_case_label(id: int) -> str:
    """
    查询案例标签。
    """
    result = await SimClient.get("/api/case/queryCaseLabel", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def bind_model_status(id: int, status: int) -> str:
    """
    绑定模型状态。
    """
    result = await SimClient.post("/api/case/bindModelStatus", data={"id": id, "status": status})
    return str(result)

@mcp.tool()
@ensure_login
async def synchronize_to_simulation_parameter(id: int) -> str:
    """
    同步到仿真参数。
    """
    result = await SimClient.post("/api/case/synchronizeToSimulationParameter", data={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_synchronize_to_simulation_parameter(id: int) -> str:
    """
    获取同步仿真参数。
    """
    result = await SimClient.get("/api/case/getSynchronizeToSimulationParameter", params={"id": id})
    return str(result)

# --- VR Path ---

@mcp.tool()
@ensure_login
async def add_vr_path_data(
    case_id: int,
    path_name: str,
    path_data: str,
    sort: int = 0
) -> str:
    """
    添加VR路径数据。
    """
    payload = {
        "caseId": case_id,
        "pathName": path_name,
        "pathData": path_data,
        "sort": sort
    }
    result = await SimClient.post("/api/case/addVrPathData", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def update_vr_path_data(
    id: int,
    path_name: Optional[str] = None,
    path_data: Optional[str] = None,
    sort: Optional[int] = None
) -> str:
    """
    更新VR路径数据。
    """
    payload = {"id": id}
    if path_name: payload["pathName"] = path_name
    if path_data: payload["pathData"] = path_data
    if sort is not None: payload["sort"] = sort
    result = await SimClient.post("/api/case/updateVrPathData", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_vr_path_data(case_id: int) -> str:
    """
    查询VR路径数据。
    """
    result = await SimClient.get("/api/case/queryVrPathData", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_vr_path_data_by_id(id: int) -> str:
    """
    根据ID查询VR路径数据。
    """
    result = await SimClient.get("/api/case/queryVrPathDataById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def delete_vr_path_data(id: int) -> str:
    """
    删除VR路径数据。
    """
    result = await SimClient.delete("/api/case/deleteVrPathData", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_vr_route(
    case_id: int,
    route_name: str,
    route_json: str,
    id: Optional[int] = None
) -> str:
    """
    保存案例VR路由。
    """
    payload = {
        "caseId": case_id,
        "routeName": route_name,
        "routeJson": route_json
    }
    if id is not None: payload["id"] = id
    result = await SimClient.post("/api/case/saveOrUpdateVrRoute", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_case_vr_route_list(case_id: int) -> str:
    """
    查询案例VR路由列表。
    """
    result = await SimClient.get("/api/case/queryCaseVrRouteDTOList", params={"caseId": case_id})
    return str(result)

# --- Playback & IoT ---

@mcp.tool()
@ensure_login
async def save_case_playback(
    case_id: int,
    id: Optional[int] = None,
    playback_name: Optional[str] = None,
    playback_type: Optional[int] = None,
    playback_speed: Optional[float] = None
) -> str:
    """
    保存或更新IoT回放。
    """
    payload = {"caseId": case_id}
    if id is not None: payload["id"] = id
    if playback_name: payload["playbackName"] = playback_name
    if playback_type is not None: payload["playbackType"] = playback_type
    if playback_speed is not None: payload["playbackSpeed"] = playback_speed
    
    result = await SimClient.post("/api/case/playback/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_playback_element(
    case_id: int,
    point_name: str,
    point_value: str,
    time: str,
    id: Optional[int] = None,
    index_code: Optional[str] = None,
    model_id: Optional[str] = None
) -> str:
    """
    保存或更新IoT回放元素。
    """
    payload = {
        "caseId": case_id,
        "pointName": point_name,
        "pointValue": point_value,
        "time": time
    }
    if id is not None: payload["id"] = id
    if index_code: payload["indexCode"] = index_code
    if model_id: payload["modelId"] = model_id
    
    result = await SimClient.post("/api/case/playback/element/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_save_case_playback_element(json_list: str) -> str:
    """
    批量保存IoT回放元素 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/case/playback/element/saveOrUpdateBatch", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def query_case_playback_list(case_id: int) -> str:
    """
    查询IoT回放列表。
    """
    result = await SimClient.post("/api/case/playback/queryByList", data={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def query_case_playback_element_list(
    case_id: int,
    point_name: Optional[str] = None,
    time: Optional[str] = None
) -> str:
    """
    查询IoT回放元素列表。
    """
    payload = {"caseId": case_id}
    if point_name: payload["pointName"] = point_name
    if time: payload["time"] = time
    result = await SimClient.post("/api/case/playback/element/queryByList", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_case_playback(id: int) -> str:
    """
    删除IoT回放。
    """
    result = await SimClient.delete("/api/case/playback/removeById", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def save_iot_case(
    case_id: int,
    graph_json: str,
    id: Optional[int] = None,
    list_json: Optional[str] = None
) -> str:
    """
    保存或更新IoT场景。
    
    Args:
        case_id: 案例ID
        graph_json: LiteGraph JSON
        id: IoT案例ID
        list_json: 关联模型列表 JSON字符串 (IotCaseModel对象列表)
    """
    import json
    payload = {
        "caseId": case_id,
        "graphJson": graph_json
    }
    if id is not None: payload["id"] = id
    if list_json:
        try:
            payload["list"] = json.loads(list_json)
        except:
            return "Error: list_json must be a valid JSON string"
            
    result = await SimClient.post("/api/case/saveOrUpdateIotCase", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_iot_litegraph_json(case_id: int, graph_json: str) -> str:
    """
    保存IoT场景LiteGraph JSON。
    """
    result = await SimClient.post("/api/case/save/iotLitegraph/json", data={"caseId": case_id, "graphJson": graph_json})
    return str(result)

@mcp.tool()
@ensure_login
async def save_point_templates(json_list: str) -> str:
    """
    保存为点位模板 (传入JSON列表字符串)。
    """
    import json
    try:
        data = json.loads(json_list)
        result = await SimClient.post("/api/case/addPointTemplate", data=data)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def save_device_point(
    index_code: str,
    device_code: str,
    production_material_code: str,
    data_source: int,
    point_list_json: str
) -> str:
    """
    保存动画驱动面板信息。
    
    Args:
        index_code: 实例主键
        device_code: 物理设备ID
        production_material_code: 待生产的物料模型code
        data_source: 数据来源（0：IOT,1:ETL）
        point_list_json: 动作驱动面板信息列表 JSON字符串
    """
    import json
    try:
        point_list = json.loads(point_list_json)
        payload = {
            "indexCode": index_code,
            "deviceCode": device_code,
            "productionMaterialCode": production_material_code,
            "dataSource": data_source,
            "list": point_list
        }
        result = await SimClient.post("/api/case/addDevicePoint", data=payload)
        return str(result)
    except Exception as e:
        return f"Error parsing JSON: {e}"

@mcp.tool()
@ensure_login
async def select_template(
    model_code: str,
    case_id: str,
    data_source: int = 0
) -> str:
    """
    选择模板。
    """
    payload = {
        "modelCode": model_code,
        "caseId": case_id,
        "dataSource": data_source
    }
    result = await SimClient.post("/api/case/selectTemplate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def select_case_device_point(index_code: str, data_source: int) -> str:
    """
    查询动画驱动面板信息。
    """
    result = await SimClient.get("/api/case/selectCaseDevicePoint", params={"indexCode": index_code, "dataSource": data_source})
    return str(result)

@mcp.tool()
@ensure_login
async def query_iot_case_details(case_id: int) -> str:
    """
    查询IoT案例明细。
    """
    result = await SimClient.get("/api/case/queryIotCaseDetails", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def obtain_case_point_information(case_id: str) -> str:
    """
    获取案例点位信息。
    """
    result = await SimClient.get("/api/case/obtainCasePointInformation", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_iot_litegraph_json(case_id: int) -> str:
    """
    获取场景的liteGraph的JSON数据。
    """
    result = await SimClient.get("/api/case/get/iotLitegraph/json", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_iot_litegraph_json_all(case_id: int) -> str:
    """
    获取场景的liteGraph的JSON数据(所有)。
    """
    result = await SimClient.get("/api/case/get/iotLitegraph/json/all", params={"caseId": case_id})
    return str(result)

# --- AGV Type Management ---

@mcp.tool()
@ensure_login
async def update_agv_type(
    id: int,
    type_name: str,
    empty_speed: float,
    loading_speed: float,
    loading_time: int,
    discharge_time: int,
    type: int,
    max_capacity: Optional[int] = None,
    repair_rate: Optional[str] = None,
    auto_lead_time: Optional[int] = None,
    collision_wait_time: Optional[int] = None,
    battery_life_time: Optional[float] = None,
    charging_time: Optional[float] = None,
    charging_station_id: Optional[str] = None,
    case_id: Optional[int] = None,
    case_name: Optional[str] = None,
    scheduling_strategy: Optional[int] = None,
    lift_speed: Optional[float] = None
) -> str:
    """
    修改AGV车类型。
    """
    payload = {
        "id": id,
        "typeName": type_name,
        "emptySpeed": empty_speed,
        "loadingSpeed": loading_speed,
        "loadingTime": loading_time,
        "dischargeTime": discharge_time,
        "type": type
    }
    if max_capacity is not None: payload["maxCapacity"] = max_capacity
    if repair_rate: payload["repairRate"] = repair_rate
    if auto_lead_time is not None: payload["autoLeadTime"] = auto_lead_time
    if collision_wait_time is not None: payload["collisionWaitTime"] = collision_wait_time
    if battery_life_time is not None: payload["batteryLifeTime"] = battery_life_time
    if charging_time is not None: payload["chargingTime"] = charging_time
    if charging_station_id: payload["chargingStationId"] = charging_station_id
    if case_id is not None: payload["caseId"] = case_id
    if case_name: payload["caseName"] = case_name
    if scheduling_strategy is not None: payload["schedulingStrategy"] = scheduling_strategy
    if lift_speed is not None: payload["liftSpeed"] = lift_speed
    
    result = await SimClient.post("/api/agvEntity/updateAgvType", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def add_agv_type(
    type_name: str,
    empty_speed: float,
    loading_speed: float,
    loading_time: int,
    discharge_time: int,
    type: int,
    max_capacity: Optional[int] = None,
    repair_rate: Optional[str] = None,
    auto_lead_time: Optional[int] = None,
    collision_wait_time: Optional[int] = None,
    battery_life_time: Optional[float] = None,
    charging_time: Optional[float] = None,
    charging_station_id: Optional[str] = None,
    case_id: Optional[int] = None,
    case_name: Optional[str] = None,
    scheduling_strategy: Optional[int] = None,
    lift_speed: Optional[float] = None
) -> str:
    """
    新增AGV车类型。
    """
    payload = {
        "typeName": type_name,
        "emptySpeed": empty_speed,
        "loadingSpeed": loading_speed,
        "loadingTime": loading_time,
        "dischargeTime": discharge_time,
        "type": type
    }
    if max_capacity is not None: payload["maxCapacity"] = max_capacity
    if repair_rate: payload["repairRate"] = repair_rate
    if auto_lead_time is not None: payload["autoLeadTime"] = auto_lead_time
    if collision_wait_time is not None: payload["collisionWaitTime"] = collision_wait_time
    if battery_life_time is not None: payload["batteryLifeTime"] = battery_life_time
    if charging_time is not None: payload["chargingTime"] = charging_time
    if charging_station_id: payload["chargingStationId"] = charging_station_id
    if case_id is not None: payload["caseId"] = case_id
    if case_name: payload["caseName"] = case_name
    if scheduling_strategy is not None: payload["schedulingStrategy"] = scheduling_strategy
    if lift_speed is not None: payload["liftSpeed"] = lift_speed
    
    result = await SimClient.post("/api/agvEntity/addAgvType", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_all_agv_type(
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    type_name: Optional[str] = None,
    case_id: Optional[int] = None,
    case_name: Optional[str] = None,
    type: Optional[int] = None
) -> str:
    """
    查询AGV类型列表。
    """
    params = {"page": page, "size": size}
    if id is not None: params["id"] = id
    if type_name: params["typeName"] = type_name
    if case_id is not None: params["caseId"] = case_id
    if case_name: params["caseName"] = case_name
    if type is not None: params["type"] = type
    
    result = await SimClient.get("/api/agvEntity/queryAllAgvType", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def query_all_agv_type_scheduling_strategy() -> str:
    """
    查询AGV类型调度策略。
    """
    result = await SimClient.get("/api/agvEntity/queryAllAgvTypeSchedulingStrategy")
    return str(result)

@mcp.tool()
@ensure_login
async def query_all_agv_type_release() -> str:
    """
    查询AGV类型发布列表。
    """
    result = await SimClient.get("/api/agvEntity/queryAllAgvTypeRelease")
    return str(result)

@mcp.tool()
@ensure_login
async def delete_agv_type(id: int) -> str:
    """
    删除AGV车类型。
    """
    result = await SimClient.delete("/api/agvEntity/deleteAgvType", params={"id": id})
    return str(result)

# --- AGV Task Detail ---

@mcp.tool()
@ensure_login
async def save_or_update_agv_task_detail(
    point_id: int,
    action_type: int,
    agv_base_task_id: int,
    id: Optional[int] = None,
    point_name: Optional[str] = None,
    material_ids: Optional[str] = None,
    sort_index: Optional[int] = None,
    task_state: Optional[int] = None,
    agv_id: Optional[int] = None,
    agv_name: Optional[str] = None
) -> str:
    """
    新增或修改AGV任务明细。
    """
    payload = {
        "pointId": point_id,
        "actionType": action_type,
        "agvBaseTaskId": agv_base_task_id
    }
    if id is not None: payload["id"] = id
    if point_name: payload["pointName"] = point_name
    if material_ids: payload["materialIds"] = material_ids
    if sort_index is not None: payload["sortIndex"] = sort_index
    if task_state is not None: payload["taskState"] = task_state
    if agv_id is not None: payload["agvId"] = agv_id
    if agv_name: payload["agvName"] = agv_name
    
    result = await SimClient.post("/api/agvBaseTaskDetail/saveOrUpdateTaskDetail", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_agv_task_detail_by_task_id(
    agv_base_task_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    point_id: Optional[int] = None,
    point_name: Optional[str] = None,
    action_type: Optional[int] = None,
    material_ids: Optional[str] = None,
    sort_index: Optional[int] = None,
    task_state: Optional[int] = None,
    agv_id: Optional[int] = None,
    agv_name: Optional[str] = None
) -> str:
    """
    根据TaskId查询AGV任务明细列表。
    """
    params = {
        "agvBaseTaskId": agv_base_task_id,
        "page": page,
        "size": size
    }
    if id is not None: params["id"] = id
    if point_id is not None: params["pointId"] = point_id
    if point_name: params["pointName"] = point_name
    if action_type is not None: params["actionType"] = action_type
    if material_ids: params["materialIds"] = material_ids
    if sort_index is not None: params["sortIndex"] = sort_index
    if task_state is not None: params["taskState"] = task_state
    if agv_id is not None: params["agvId"] = agv_id
    if agv_name: params["agvName"] = agv_name
    
    result = await SimClient.get("/api/agvBaseTaskDetail/queryTaskDetailByTaskId", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_agv_task_detail(
    id: int,
    point_id: int,
    action_type: int,
    agv_base_task_id: int,
    point_name: Optional[str] = None,
    material_ids: Optional[str] = None,
    sort_index: Optional[int] = None,
    task_state: Optional[int] = None,
    agv_id: Optional[int] = None,
    agv_name: Optional[str] = None
) -> str:
    """
    删除AGV任务明细。
    """
    payload = {
        "id": id,
        "pointId": point_id,
        "actionType": action_type,
        "agvBaseTaskId": agv_base_task_id
    }
    if point_name: payload["pointName"] = point_name
    if material_ids: payload["materialIds"] = material_ids
    if sort_index is not None: payload["sortIndex"] = sort_index
    if task_state is not None: payload["taskState"] = task_state
    if agv_id is not None: payload["agvId"] = agv_id
    if agv_name: payload["agvName"] = agv_name
    
    result = await SimClient.delete("/api/agvBaseTaskDetail/deleteTask", data=payload)
    return str(result)

# --- AGV Task ---

@mcp.tool()
@ensure_login
async def save_or_update_agv_task(
    agv_type_id: str,
    case_id: int,
    id: Optional[int] = None,
    task_name: Optional[str] = None,
    task_type: Optional[str] = None,
    agv_type_name: Optional[str] = None,
    task_state: Optional[int] = None,
    task_type_level: Optional[int] = None,
    agv_id: Optional[int] = None,
    agv_name: Optional[str] = None,
    sort_index: Optional[int] = None,
    execute_times: Optional[int] = None
) -> str:
    """
    新增或修改AGV任务。
    """
    payload = {
        "agvTypeId": agv_type_id,
        "caseId": case_id
    }
    if id is not None: payload["id"] = id
    if task_name: payload["taskName"] = task_name
    if task_type: payload["taskType"] = task_type
    if agv_type_name: payload["agvTypeName"] = agv_type_name
    if task_state is not None: payload["taskState"] = task_state
    if task_type_level is not None: payload["taskTypeLevel"] = task_type_level
    if agv_id is not None: payload["agvId"] = agv_id
    if agv_name: payload["agvName"] = agv_name
    if sort_index is not None: payload["sortIndex"] = sort_index
    if execute_times is not None: payload["executeTimes"] = execute_times
    
    result = await SimClient.post("/api/agvBaseTask/saveOrUpdateTask", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_agv_task_by_case_id(
    case_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    task_name: Optional[str] = None,
    task_type: Optional[str] = None,
    agv_type_name: Optional[str] = None,
    task_state: Optional[int] = None,
    agv_type_id: Optional[str] = None,
    task_type_level: Optional[int] = None,
    agv_id: Optional[int] = None,
    agv_name: Optional[str] = None,
    sort_index: Optional[int] = None,
    execute_times: Optional[int] = None
) -> str:
    """
    根据案例ID查询AGV任务列表。
    """
    params = {
        "caseId": case_id,
        "page": page,
        "size": size
    }
    if id is not None: params["id"] = id
    if task_name: params["taskName"] = task_name
    if task_type: params["taskType"] = task_type
    if agv_type_name: params["agvTypeName"] = agv_type_name
    if task_state is not None: params["taskState"] = task_state
    if agv_type_id: params["agvTypeId"] = agv_type_id
    if task_type_level is not None: params["taskTypeLevel"] = task_type_level
    if agv_id is not None: params["agvId"] = agv_id
    if agv_name: params["agvName"] = agv_name
    if sort_index is not None: params["sortIndex"] = sort_index
    if execute_times is not None: params["executeTimes"] = execute_times
    
    result = await SimClient.get("/api/agvBaseTask/queryTaskByCaseId", params=params)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_agv_task(id: int) -> str:
    """
    删除AGV任务。
    """
    result = await SimClient.delete("/api/agvBaseTask/deleteTask", params={"id": id})
    return str(result)

# --- AGV Info ---

@mcp.tool()
@ensure_login
async def save_agv_info(
    agv_type_id: int,
    agv_name: str,
    case_id: int,
    id: Optional[int] = None
) -> str:
    """
    保存AGV信息。
    """
    payload = {
        "agvTypeId": agv_type_id,
        "agvName": agv_name,
        "caseId": case_id
    }
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/agv/saveAgvInfo", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_agv_info(case_id: int) -> str:
    """
    获取AGV信息列表。
    """
    result = await SimClient.get("/api/agv/getAgvInfo", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_agv_run_stats(case_id: int) -> str:
    """
    获取AGV运行统计信息。
    """
    result = await SimClient.get("/api/agv/stats/runStats", params={"caseId": case_id})
    return str(result)

# --- Unit Management ---

@mcp.tool()
@ensure_login
async def update_case_unit(case_id: int, unit_category: str, unit: str) -> str:
    """
    更新场景默认单位。
    """
    payload = {
        "场景ID": case_id,
        "单位类别": unit_category,
        "单位": unit
    }
    result = await SimClient.post("/api/v7/caseUnit/update", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def init_unit() -> str:
    """
    初始化可用单位入库。
    """
    result = await SimClient.post("/api/v4/unit/init")
    return str(result)

@mcp.tool()
@ensure_login
async def get_case_unit_category_list(case_id: int) -> str:
    """
    场景单位分类列表。
    """
    result = await SimClient.get("/api/v7/caseUnit/category/list", params={"caseId": case_id})
    return str(result)

# --- Tool Controller ---

@mcp.tool()
@ensure_login
async def save_tool_request(params: str) -> str:
    """
    保存请求。
    """
    payload = {"params": params}
    result = await SimClient.post("/api/tool/saveRequest", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def init_project(
    update_chunk_ids: List[int],
    inset_chunk_ids: List[int],
    sim_url: str,
    sim_username: str,
    sim_password: str
) -> str:
    """
    项目更新数据功能。
    """
    payload = {
        "updateChunkIds": update_chunk_ids,
        "insetChunkIds": inset_chunk_ids,
        "simUrl": sim_url,
        "simUsername": sim_username,
        "simPassword": sim_password
    }
    result = await SimClient.post("/api/tool/initProject", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_scenes_by_chunk_ids(chunk_ids: List[int]) -> str:
    """
    根据块id获取场景信息。
    """
    result = await SimClient.post("/api/tool/getScenesByChunkIds", data=chunk_ids)
    return str(result)

# --- Worker Task Craft Routing ---

@mcp.tool()
@ensure_login
async def save_or_update_worker_task_craft_routing(
    case_id: int,
    task_id: int,
    craft_routing_id: int,
    id: Optional[int] = None,
    sim_case_id: Optional[int] = None
) -> str:
    """
    新增或编辑工人加工工步配置。
    """
    payload = {
        "caseId": case_id,
        "taskId": task_id,
        "craftRoutingId": craft_routing_id
    }
    if id is not None: payload["id"] = id
    if sim_case_id is not None: payload["simCaseId"] = sim_case_id
    
    result = await SimClient.post("/api/simWorkerTaskCraftRouting/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def batch_save_worker_task_craft_routing(
    case_id: int,
    task_id: int,
    craft_routing_list: List[Dict[str, Any]]
) -> str:
    """
    批量新增或编辑工人加工工步配置。
    """
    payload = {
        "caseId": case_id,
        "taskId": task_id,
        "list": craft_routing_list
    }
    result = await SimClient.post("/api/simWorkerTaskCraftRouting/saveOrUpdateBatch", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_worker_task_craft_routing_by_page(
    case_id: int,
    task_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    sim_case_id: Optional[int] = None,
    craft_routing_id: Optional[int] = None
) -> str:
    """
    获取工人加工工步配置分页数据。
    """
    payload = {
        "caseId": case_id,
        "taskId": task_id,
        "page": page,
        "size": size
    }
    if id is not None: payload["id"] = id
    if sim_case_id is not None: payload["simCaseId"] = sim_case_id
    if craft_routing_id is not None: payload["craftRoutingId"] = craft_routing_id
    
    result = await SimClient.post("/api/simWorkerTaskCraftRouting/queryByPage", data=payload)
    return str(result)

# --- Worker Point and Path Management ---

@mcp.tool()
@ensure_login
async def save_worker_point_and_path(
    case_id: int,
    point_list: List[Dict[str, Any]],
    path_list: List[Dict[str, Any]]
) -> str:
    """
    保存或修改工人点位和路径。
    """
    payload = {
        "caseId": case_id,
        "pointList": point_list,
        "pathList": path_list
    }
    result = await SimClient.post("/api/simWorker/savePointAndPath", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_worker_point_and_path(case_id: int) -> str:
    """
    获取工人点位和路径。
    """
    result = await SimClient.get("/api/simWorker/getPointAndPath", params={"caseId": case_id})
    return str(result)

# --- Process Drawing ---

@mcp.tool()
@ensure_login
async def save_process_drawing(case_id: int, draw_json: str, material_code: str) -> str:
    """
    保存工艺一张图。
    """
    payload = {
        "caseId": case_id,
        "drawJson": draw_json,
        "materialCode": material_code
    }
    result = await SimClient.post("/api/simProcessDrawing/save", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_process_drawing(case_id: int, material_code: str) -> str:
    """
    获取工艺一张图。
    """
    result = await SimClient.get("/api/simProcessDrawing/query", params={"caseId": case_id, "materialCode": material_code})
    return str(result)

@mcp.tool()
@ensure_login
async def get_process_drawing_production_list(case_id: int) -> str:
    """
    获取工艺一张图产品列表。
    """
    result = await SimClient.get("/api/simProcessDrawing/productionList", params={"caseId": case_id})
    return str(result)

# --- Expression Template ---

@mcp.tool()
@ensure_login
async def save_or_update_expression_template(
    template_name: str,
    expression: str,
    id: Optional[int] = None
) -> str:
    """
    保存或更新表达式模板。
    """
    payload = {
        "templateName": template_name,
        "expression": expression
    }
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/simExpressionTemplate/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_expression_template(id: int) -> str:
    """
    删除表达式模板。
    """
    payload = {"id": id}
    result = await SimClient.post("/api/simExpressionTemplate/delete", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def check_expression(case_id: int, web_uuid: str, param_key: str, expression: str) -> str:
    """
    表达式校验。
    """
    payload = {
        "caseId": case_id,
        "webUuid": web_uuid,
        "paramKey": param_key,
        "expression": expression
    }
    result = await SimClient.post("/api/simExpressionTemplate/check", data=payload)
    return str(result)

# --- Factory Calendar ---

@mcp.tool()
@ensure_login
async def use_case_schedule(case_id: int, schedule_ids: Optional[List[int]] = None) -> str:
    """
    批量应用班次时间。
    """
    payload = {"caseId": case_id}
    if schedule_ids: payload["scheduleIds"] = schedule_ids
    
    result = await SimClient.post("/api/simCaseSchedule/use", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def change_case_schedule(case_id: int, schedule_id: int) -> str:
    """
    切换应用班次。
    """
    payload = {
        "caseId": case_id,
        "scheduleId": schedule_id
    }
    result = await SimClient.post("/api/simCaseSchedule/use/change", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_case_schedule(
    case_id: int,
    schedule_name: str,
    start_time: Dict[str, int],
    end_time: Dict[str, int],
    week_day: str,
    pause_time: Optional[str] = None,
    apply_outline: Optional[str] = None,
    in_use: Optional[bool] = None,
    id: Optional[int] = None
) -> str:
    """
    保存或修改班次时间。
    """
    payload = {
        "caseId": case_id,
        "scheduleName": schedule_name,
        "startTime": start_time,
        "endTime": end_time,
        "weekDay": week_day
    }
    if pause_time: payload["pauseTime"] = pause_time
    if apply_outline: payload["applyOutline"] = apply_outline
    if in_use is not None: payload["inUse"] = in_use
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/simCaseSchedule/save", data=payload)
    return str(result)

# --- Simulation Run Stats ---

@mcp.tool()
@ensure_login
async def update_report_name(case_id: int, unique_id: str, case_unique_name: str) -> str:
    """
    更新报表名称。
    """
    payload = {
        "caseId": case_id,
        "uniqueId": unique_id,
        "caseUniqueName": case_unique_name
    }
    result = await SimClient.post("/api/simCaseRunStats/updateReportName", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_time_queue_size(case_id: int, unique_id: str, index_codes: List[str]) -> str:
    """
    获取在制品数量变化。
    """
    payload = {
        "caseId": case_id,
        "uniqueId": unique_id,
        "indexCode": index_codes
    }
    result = await SimClient.post("/api/simCaseRunStats/timeQueueSize", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_time_queue_size_real_time(case_id: int, unique_id: str, index_codes: List[str]) -> str:
    """
    获取在制品实时数量变化。
    """
    payload = {
        "caseId": case_id,
        "uniqueId": unique_id,
        "indexCode": index_codes
    }
    result = await SimClient.post("/api/simCaseRunStats/timeQueueSizeRealTime", data=payload)
    return str(result)

# --- Process Route Map ---

@mcp.tool()
@ensure_login
async def update_process_route_map(
    case_id: int,
    material_code: str,
    process_route_map: str
) -> str:
    """
    更新工艺路线图。
    """
    payload = {
        "caseId": case_id,
        "materialCode": material_code,
        "processRouteMap": process_route_map
    }
    result = await SimClient.post("/api/simProcessRouteMap/update", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_process_route_map(case_id: int, material_code: str) -> str:
    """
    获取工艺路线图。
    """
    result = await SimClient.get("/api/simProcessRouteMap/get", params={"caseId": case_id, "materialCode": material_code})
    return str(result)

# --- Simulation Parameter Template ---

@mcp.tool()
@ensure_login
async def save_or_update_param_template(
    case_id: int,
    template_name: str,
    id: Optional[int] = None
) -> str:
    """
    保存或修改参数模板。
    """
    payload = {
        "caseId": case_id,
        "templateName": template_name
    }
    if id is not None: payload["id"] = id
    
    result = await SimClient.post("/api/simCaseModelParamTemplate/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def delete_param_template(id: int) -> str:
    """
    删除参数模板。
    """
    result = await SimClient.delete("/api/simCaseModelParamTemplate/delete", params={"id": id})
    return str(result)

@mcp.tool()
@ensure_login
async def use_param_template(case_id: int, template_id: int) -> str:
    """
    应用参数模板。
    """
    payload = {
        "caseId": case_id,
        "templateId": template_id
    }
    result = await SimClient.post("/api/simCaseModelParamTemplate/use", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def export_param_template(case_id: int, template_id: int) -> str:
    """
    导出参数模板。
    """
    result = await SimClient.get("/api/simCaseModelParamTemplate/export", params={"req": {"caseId": case_id, "templateId": template_id}})
    return str(result)

@mcp.tool()
@ensure_login
async def get_param_template_list(case_id: int) -> str:
    """
    参数模板列表。
    """
    result = await SimClient.get("/api/simCaseModelParamTemplate/list", params={"caseId": case_id})
    return str(result)

@mcp.tool()
@ensure_login
async def get_param_template_category_list(case_id: int, template_id: Optional[int] = None) -> str:
    """
    参数模板分类列表。
    """
    params = {"caseId": case_id}
    if template_id is not None: params["templateId"] = template_id
    
    result = await SimClient.get("/api/simCaseModelParamTemplate/categoryList", params=params)
    return str(result)

# --- Model Management ---

@mcp.tool()
@ensure_login
async def update_model_graph_json(case_id: int, index_code: str, graph_json: str) -> str:
    """
    更新模型的graphJson。
    """
    payload = {
        "案例id": case_id,
        "场景模型的唯一值indexCode": index_code,
        "模型的graphJSon": graph_json
    }
    result = await SimClient.post("/api/simCaseModel/updateGraphJson", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def save_model_param_config(
    case_id: int,
    model_uuid: str,
    model_type: str,
    model_config_params: List[Dict[str, Any]],
    param_template_id: Optional[int] = None
) -> str:
    """
    场景内保存模型参数配置。
    """
    payload = {
        "场景id": case_id,
        "模型uuid": model_uuid,
        "模型类型": model_type,
        "模型配置参数": model_config_params
    }
    if param_template_id is not None: payload["参数模板id"] = param_template_id
    
    result = await SimClient.post("/api/simCaseModel/param/save", data=payload)
    return str(result)

# --- Master Data Management ---

# --- Master Data - Work Center ---

@mcp.tool()
@ensure_login
async def save_or_update_master_data_work_center(
    work_center_code: str,
    work_center_name: str,
    super_id: int,
    id: Optional[int] = None,
    work_center_type: Optional[str] = None,
    usage_type: Optional[str] = None,
    status: Optional[str] = None,
    asset_code: Optional[str] = None,
    asset_manager_id: Optional[str] = None,
    asset_manager_name: Optional[str] = None,
    procurement_method: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑工作中心数据。
    """
    payload = {
        "workCenterCode": work_center_code,
        "workCenterName": work_center_name,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if work_center_type is not None: payload["workCenterType"] = work_center_type
    if usage_type is not None: payload["usageType"] = usage_type
    if status is not None: payload["status"] = status
    if asset_code is not None: payload["assetCode"] = asset_code
    if asset_manager_id is not None: payload["assetManagerId"] = asset_manager_id
    if asset_manager_name is not None: payload["assetManagerName"] = asset_manager_name
    if procurement_method is not None: payload["procurementMethod"] = procurement_method
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataWorkCenter/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_work_center_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    work_center_code: Optional[str] = None,
    work_center_name: Optional[str] = None,
    work_center_type: Optional[str] = None,
    usage_type: Optional[str] = None,
    status: Optional[str] = None,
    asset_code: Optional[str] = None,
    asset_manager_id: Optional[str] = None,
    asset_manager_name: Optional[str] = None,
    procurement_method: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取工作中心分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if work_center_code is not None: payload["workCenterCode"] = work_center_code
    if work_center_name is not None: payload["workCenterName"] = work_center_name
    if work_center_type is not None: payload["workCenterType"] = work_center_type
    if usage_type is not None: payload["usageType"] = usage_type
    if status is not None: payload["status"] = status
    if asset_code is not None: payload["assetCode"] = asset_code
    if asset_manager_id is not None: payload["assetManagerId"] = asset_manager_id
    if asset_manager_name is not None: payload["assetManagerName"] = asset_manager_name
    if procurement_method is not None: payload["procurementMethod"] = procurement_method
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataWorkCenter/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_work_center_by_list(
    work_center_code: str,
    work_center_name: str,
    super_id: int,
    id: Optional[int] = None,
    work_center_type: Optional[str] = None,
    usage_type: Optional[str] = None,
    status: Optional[str] = None,
    asset_code: Optional[str] = None,
    asset_manager_id: Optional[str] = None,
    asset_manager_name: Optional[str] = None,
    procurement_method: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    通过条件查询工作中心批量数据。
    """
    payload = {
        "workCenterCode": work_center_code,
        "workCenterName": work_center_name,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if work_center_type is not None: payload["workCenterType"] = work_center_type
    if usage_type is not None: payload["usageType"] = usage_type
    if status is not None: payload["status"] = status
    if asset_code is not None: payload["assetCode"] = asset_code
    if asset_manager_id is not None: payload["assetManagerId"] = asset_manager_id
    if asset_manager_name is not None: payload["assetManagerName"] = asset_manager_name
    if procurement_method is not None: payload["procurementMethod"] = procurement_method
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataWorkCenter/queryByList", data=payload)
    return str(result)

# --- Master Data - Process Route ---

@mcp.tool()
@ensure_login
async def save_or_update_master_data_process_route(
    equipment_code: str,
    equipment_name: str,
    process_name: str,
    process_hours: str,
    is_common: int,
    super_id: int,
    id: Optional[int] = None,
    unit: Optional[int] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑工艺路线数据。
    """
    payload = {
        "equipmentCode": equipment_code,
        "equipmentName": equipment_name,
        "processName": process_name,
        "processHours": process_hours,
        "isCommon": is_common,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if unit is not None: payload["unit"] = unit
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataProcessRoute/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_process_route_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    equipment_code: Optional[str] = None,
    equipment_name: Optional[str] = None,
    process_name: Optional[str] = None,
    process_hours: Optional[str] = None,
    unit: Optional[int] = None,
    is_common: Optional[int] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取工艺路线分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if equipment_code is not None: payload["equipmentCode"] = equipment_code
    if equipment_name is not None: payload["equipmentName"] = equipment_name
    if process_name is not None: payload["processName"] = process_name
    if process_hours is not None: payload["processHours"] = process_hours
    if unit is not None: payload["unit"] = unit
    if is_common is not None: payload["isCommon"] = is_common
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataProcessRoute/queryByPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_process_route_by_list(
    equipment_code: str,
    equipment_name: str,
    process_name: str,
    process_hours: str,
    is_common: int,
    super_id: int,
    id: Optional[int] = None,
    unit: Optional[int] = None,
    company_id: Optional[int] = None
) -> str:
    """
    通过条件查询工艺路线批量数据。
    """
    payload = {
        "equipmentCode": equipment_code,
        "equipmentName": equipment_name,
        "processName": process_name,
        "processHours": process_hours,
        "isCommon": is_common,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if unit is not None: payload["unit"] = unit
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataProcessRoute/queryByList", data=payload)
    return str(result)

# --- Master Data - Material Master Data ---

@mcp.tool()
@ensure_login
async def save_or_update_master_data_material(
    material_code: str,
    material_name: str,
    super_id: int,
    id: Optional[int] = None,
    material_group_code: Optional[str] = None,
    material_group_name: Optional[str] = None,
    specification: Optional[str] = None,
    material_type: Optional[str] = None,
    material_type_name: Optional[str] = None,
    manufacturing_method: Optional[str] = None,
    manufacturing_method_name: Optional[str] = None,
    unit_code: Optional[str] = None,
    unit_name: Optional[str] = None,
    description: Optional[str] = None,
    barcode_management: Optional[str] = None,
    has_carton_barcode: Optional[int] = None,
    pallet_layer_quantity: Optional[int] = None,
    carton_length_mm: Optional[str] = None,
    carton_width_mm: Optional[str] = None,
    carton_height_mm: Optional[str] = None,
    full_pallet_quantity: Optional[int] = None,
    gross_weight_g: Optional[str] = None,
    inventory_alert_quantity: Optional[int] = None,
    supplier_material_code: Optional[str] = None,
    supplier_material_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑物料主数据。
    """
    payload = {
        "materialCode": material_code,
        "materialName": material_name,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if material_group_code is not None: payload["materialGroupCode"] = material_group_code
    if material_group_name is not None: payload["materialGroupName"] = material_group_name
    if specification is not None: payload["specification"] = specification
    if material_type is not None: payload["materialType"] = material_type
    if material_type_name is not None: payload["materialTypeName"] = material_type_name
    if manufacturing_method is not None: payload["manufacturingMethod"] = manufacturing_method
    if manufacturing_method_name is not None: payload["manufacturingMethodName"] = manufacturing_method_name
    if unit_code is not None: payload["unitCode"] = unit_code
    if unit_name is not None: payload["unitName"] = unit_name
    if description is not None: payload["description"] = description
    if barcode_management is not None: payload["barcodeManagement"] = barcode_management
    if has_carton_barcode is not None: payload["hasCartonBarcode"] = has_carton_barcode
    if pallet_layer_quantity is not None: payload["palletLayerQuantity"] = pallet_layer_quantity
    if carton_length_mm is not None: payload["cartonLengthMm"] = carton_length_mm
    if carton_width_mm is not None: payload["cartonWidthMm"] = carton_width_mm
    if carton_height_mm is not None: payload["cartonHeightMm"] = carton_height_mm
    if full_pallet_quantity is not None: payload["fullPalletQuantity"] = full_pallet_quantity
    if gross_weight_g is not None: payload["grossWeightG"] = gross_weight_g
    if inventory_alert_quantity is not None: payload["inventoryAlertQuantity"] = inventory_alert_quantity
    if supplier_material_code is not None: payload["supplierMaterialCode"] = supplier_material_code
    if supplier_material_name is not None: payload["supplierMaterialName"] = supplier_material_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataMaterialMasterData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_material_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    material_code: Optional[str] = None,
    material_name: Optional[str] = None,
    material_group_code: Optional[str] = None,
    material_group_name: Optional[str] = None,
    specification: Optional[str] = None,
    material_type: Optional[str] = None,
    material_type_name: Optional[str] = None,
    manufacturing_method: Optional[str] = None,
    manufacturing_method_name: Optional[str] = None,
    unit_code: Optional[str] = None,
    unit_name: Optional[str] = None,
    description: Optional[str] = None,
    barcode_management: Optional[str] = None,
    has_carton_barcode: Optional[int] = None,
    pallet_layer_quantity: Optional[int] = None,
    carton_length_mm: Optional[str] = None,
    carton_width_mm: Optional[str] = None,
    carton_height_mm: Optional[str] = None,
    full_pallet_quantity: Optional[int] = None,
    gross_weight_g: Optional[str] = None,
    inventory_alert_quantity: Optional[int] = None,
    supplier_material_code: Optional[str] = None,
    supplier_material_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取物料主数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if material_code is not None: payload["materialCode"] = material_code
    if material_name is not None: payload["materialName"] = material_name
    if material_group_code is not None: payload["materialGroupCode"] = material_group_code
    if material_group_name is not None: payload["materialGroupName"] = material_group_name
    if specification is not None: payload["specification"] = specification
    if material_type is not None: payload["materialType"] = material_type
    if material_type_name is not None: payload["materialTypeName"] = material_type_name
    if manufacturing_method is not None: payload["manufacturingMethod"] = manufacturing_method
    if manufacturing_method_name is not None: payload["manufacturingMethodName"] = manufacturing_method_name
    if unit_code is not None: payload["unitCode"] = unit_code
    if unit_name is not None: payload["unitName"] = unit_name
    if description is not None: payload["description"] = description
    if barcode_management is not None: payload["barcodeManagement"] = barcode_management
    if has_carton_barcode is not None: payload["hasCartonBarcode"] = has_carton_barcode
    if pallet_layer_quantity is not None: payload["palletLayerQuantity"] = pallet_layer_quantity
    if carton_length_mm is not None: payload["cartonLengthMm"] = carton_length_mm
    if carton_width_mm is not None: payload["cartonWidthMm"] = carton_width_mm
    if carton_height_mm is not None: payload["cartonHeightMm"] = carton_height_mm
    if full_pallet_quantity is not None: payload["fullPalletQuantity"] = full_pallet_quantity
    if gross_weight_g is not None: payload["grossWeightG"] = gross_weight_g
    if inventory_alert_quantity is not None: payload["inventoryAlertQuantity"] = inventory_alert_quantity
    if supplier_material_code is not None: payload["supplierMaterialCode"] = supplier_material_code
    if supplier_material_name is not None: payload["supplierMaterialName"] = supplier_material_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataMaterialMasterData/queryByPage", data=payload)
    return str(result)

# --- Master Data - Equipment Master Data ---

@mcp.tool()
@ensure_login
async def save_or_update_master_data_equipment(
    equipment_code: str,
    equipment_name: str,
    super_id: int,
    id: Optional[int] = None,
    equipment_abbreviation: Optional[str] = None,
    equipment_type_code: Optional[str] = None,
    equipment_type_name: Optional[str] = None,
    equipment_model_code: Optional[str] = None,
    equipment_model_name: Optional[str] = None,
    status: Optional[str] = None,
    iot_status: Optional[str] = None,
    operation_status: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑设备档案数据。
    """
    payload = {
        "equipmentCode": equipment_code,
        "equipmentName": equipment_name,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if equipment_abbreviation is not None: payload["equipmentAbbreviation"] = equipment_abbreviation
    if equipment_type_code is not None: payload["equipmentTypeCode"] = equipment_type_code
    if equipment_type_name is not None: payload["equipmentTypeName"] = equipment_type_name
    if equipment_model_code is not None: payload["equipmentModelCode"] = equipment_model_code
    if equipment_model_name is not None: payload["equipmentModelName"] = equipment_model_name
    if status is not None: payload["status"] = status
    if iot_status is not None: payload["iotStatus"] = iot_status
    if operation_status is not None: payload["operationStatus"] = operation_status
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataEquipmentMasterData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_equipment_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    equipment_code: Optional[str] = None,
    equipment_name: Optional[str] = None,
    equipment_abbreviation: Optional[str] = None,
    equipment_type_code: Optional[str] = None,
    equipment_type_name: Optional[str] = None,
    equipment_model_code: Optional[str] = None,
    equipment_model_name: Optional[str] = None,
    status: Optional[str] = None,
    iot_status: Optional[str] = None,
    operation_status: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取设备档案分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if equipment_code is not None: payload["equipmentCode"] = equipment_code
    if equipment_name is not None: payload["equipmentName"] = equipment_name
    if equipment_abbreviation is not None: payload["equipmentAbbreviation"] = equipment_abbreviation
    if equipment_type_code is not None: payload["equipmentTypeCode"] = equipment_type_code
    if equipment_type_name is not None: payload["equipmentTypeName"] = equipment_type_name
    if equipment_model_code is not None: payload["equipmentModelCode"] = equipment_model_code
    if equipment_model_name is not None: payload["equipmentModelName"] = equipment_model_name
    if status is not None: payload["status"] = status
    if iot_status is not None: payload["iotStatus"] = iot_status
    if operation_status is not None: payload["operationStatus"] = operation_status
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/masterDataEquipmentMasterData/queryByPage", data=payload)
    return str(result)

# --- Master Data - BOM Master Data ---

@mcp.tool()
@ensure_login
async def save_or_update_master_data_bom(
    material_code: str,
    material_name: str,
    bom_version: str,
    status: str,
    consumption_rate: str,
    pid: int,
    super_id: int,
    id: Optional[int] = None,
    material_type_code: Optional[str] = None,
    material_type_name: Optional[str] = None,
    manufacturing_method_name: Optional[str] = None,
    material_group_code: Optional[str] = None,
    material_group_name: Optional[str] = None,
    unit: Optional[str] = None,
    advance_stock_lead_time: Optional[int] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    main_product: Optional[int] = None,
    company_id: Optional[int] = None,
    bom_level: Optional[int] = None
) -> str:
    """
    新增或编辑BOM主数据。
    """
    payload = {
        "materialCode": material_code,
        "materialName": material_name,
        "bomVersion": bom_version,
        "status": status,
        "consumptionRate": consumption_rate,
        "pid": pid,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if material_type_code is not None: payload["materialTypeCode"] = material_type_code
    if material_type_name is not None: payload["materialTypeName"] = material_type_name
    if manufacturing_method_name is not None: payload["manufacturingMethodName"] = manufacturing_method_name
    if material_group_code is not None: payload["materialGroupCode"] = material_group_code
    if material_group_name is not None: payload["materialGroupName"] = material_group_name
    if unit is not None: payload["unit"] = unit
    if advance_stock_lead_time is not None: payload["advanceStockLeadTime"] = advance_stock_lead_time
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if main_product is not None: payload["mainProduct"] = main_product
    if company_id is not None: payload["companyId"] = company_id
    if bom_level is not None: payload["bomLevel"] = bom_level
    
    result = await SimClient.post("/api/masterDataBomMasterData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_master_data_bom_by_page(
    pid: int,
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    material_code: Optional[str] = None,
    material_name: Optional[str] = None,
    bom_version: Optional[str] = None,
    status: Optional[str] = None,
    material_type_code: Optional[str] = None,
    material_type_name: Optional[str] = None,
    manufacturing_method_name: Optional[str] = None,
    material_group_code: Optional[str] = None,
    material_group_name: Optional[str] = None,
    consumption_rate: Optional[str] = None,
    unit: Optional[str] = None,
    advance_stock_lead_time: Optional[int] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    main_product: Optional[int] = None,
    company_id: Optional[int] = None,
    bom_level: Optional[int] = None
) -> str:
    """
    获取BOM主数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "pid": pid,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if material_code is not None: payload["materialCode"] = material_code
    if material_name is not None: payload["materialName"] = material_name
    if bom_version is not None: payload["bomVersion"] = bom_version
    if status is not None: payload["status"] = status
    if material_type_code is not None: payload["materialTypeCode"] = material_type_code
    if material_type_name is not None: payload["materialTypeName"] = material_type_name
    if manufacturing_method_name is not None: payload["manufacturingMethodName"] = manufacturing_method_name
    if material_group_code is not None: payload["materialGroupCode"] = material_group_code
    if material_group_name is not None: payload["materialGroupName"] = material_group_name
    if consumption_rate is not None: payload["consumptionRate"] = consumption_rate
    if unit is not None: payload["unit"] = unit
    if advance_stock_lead_time is not None: payload["advanceStockLeadTime"] = advance_stock_lead_time
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if main_product is not None: payload["mainProduct"] = main_product
    if company_id is not None: payload["companyId"] = company_id
    if bom_level is not None: payload["bomLevel"] = bom_level
    
    result = await SimClient.post("/api/masterDataBomMasterData/queryByPage", data=payload)
    return str(result)

# --- Business Data Management ---

# --- Business Data - Standard Time ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_standard_time(
    equipment_code: str,
    equipment_name: str,
    beat_quantity: str,
    output_material_code: str,
    output_material_name: str,
    super_id: int,
    id: Optional[int] = None,
    workshop_code: Optional[str] = None,
    workshop_name: Optional[str] = None,
    beat_unit: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑标准工时数据。
    """
    payload = {
        "equipmentCode": equipment_code,
        "equipmentName": equipment_name,
        "beatQuantity": beat_quantity,
        "outputMaterialCode": output_material_code,
        "outputMaterialName": output_material_name,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if workshop_code is not None: payload["workshopCode"] = workshop_code
    if workshop_name is not None: payload["workshopName"] = workshop_name
    if beat_unit is not None: payload["beatUnit"] = beat_unit
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataStandardTime/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_standard_time_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    equipment_code: Optional[str] = None,
    equipment_name: Optional[str] = None,
    beat_quantity: Optional[str] = None,
    output_material_code: Optional[str] = None,
    output_material_name: Optional[str] = None,
    workshop_code: Optional[str] = None,
    workshop_name: Optional[str] = None,
    beat_unit: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取标准工时分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if equipment_code is not None: payload["equipmentCode"] = equipment_code
    if equipment_name is not None: payload["equipmentName"] = equipment_name
    if beat_quantity is not None: payload["beatQuantity"] = beat_quantity
    if output_material_code is not None: payload["outputMaterialCode"] = output_material_code
    if output_material_name is not None: payload["outputMaterialName"] = output_material_name
    if workshop_code is not None: payload["workshopCode"] = workshop_code
    if workshop_name is not None: payload["workshopName"] = workshop_name
    if beat_unit is not None: payload["beatUnit"] = beat_unit
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataStandardTime/queryByPage", data=payload)
    return str(result)

# --- Business Data - Scheduling Data ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_scheduling(
    production_order_code: str,
    product_code: str,
    product_name: str,
    workshop_code: str,
    production_line_code: str,
    planned_start_date: str,
    planned_end_date: str,
    planned_quantity: int,
    super_id: int,
    id: Optional[int] = None,
    work_order_code: Optional[str] = None,
    work_order_status: Optional[str] = None,
    actual_quantity: Optional[int] = None,
    qualified_quantity: Optional[int] = None,
    repaired_quantity: Optional[int] = None,
    rejected_quantity: Optional[int] = None,
    actual_start_date: Optional[str] = None,
    actual_end_date: Optional[str] = None,
    process_code: Optional[str] = None,
    process_name: Optional[str] = None,
    process_version: Optional[str] = None,
    unit: Optional[str] = None,
    unit_code: Optional[str] = None,
    production_order_type: Optional[str] = None,
    reporting_type: Optional[str] = None,
    reporting_method: Optional[str] = None,
    is_team_task: Optional[int] = None,
    defect_handling_type: Optional[str] = None,
    rework_type: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑排产数据。
    """
    payload = {
        "productionOrderCode": production_order_code,
        "productCode": product_code,
        "productName": product_name,
        "workshopCode": workshop_code,
        "productionLineCode": production_line_code,
        "plannedStartDate": planned_start_date,
        "plannedEndDate": planned_end_date,
        "plannedQuantity": planned_quantity,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if work_order_code is not None: payload["workOrderCode"] = work_order_code
    if work_order_status is not None: payload["workOrderStatus"] = work_order_status
    if actual_quantity is not None: payload["actualQuantity"] = actual_quantity
    if qualified_quantity is not None: payload["qualifiedQuantity"] = qualified_quantity
    if repaired_quantity is not None: payload["repairedQuantity"] = repaired_quantity
    if rejected_quantity is not None: payload["rejectedQuantity"] = rejected_quantity
    if actual_start_date is not None: payload["actualStartDate"] = actual_start_date
    if actual_end_date is not None: payload["actualEndDate"] = actual_end_date
    if process_code is not None: payload["processCode"] = process_code
    if process_name is not None: payload["processName"] = process_name
    if process_version is not None: payload["processVersion"] = process_version
    if unit is not None: payload["unit"] = unit
    if unit_code is not None: payload["unitCode"] = unit_code
    if production_order_type is not None: payload["productionOrderType"] = production_order_type
    if reporting_type is not None: payload["reportingType"] = reporting_type
    if reporting_method is not None: payload["reportingMethod"] = reporting_method
    if is_team_task is not None: payload["isTeamTask"] = is_team_task
    if defect_handling_type is not None: payload["defectHandlingType"] = defect_handling_type
    if rework_type is not None: payload["reworkType"] = rework_type
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataSchedulingData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_scheduling_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    work_order_code: Optional[str] = None,
    production_order_code: Optional[str] = None,
    product_code: Optional[str] = None,
    product_name: Optional[str] = None,
    workshop_code: Optional[str] = None,
    production_line_code: Optional[str] = None,
    planned_start_date: Optional[str] = None,
    planned_end_date: Optional[str] = None,
    planned_quantity: Optional[int] = None,
    work_order_status: Optional[str] = None,
    actual_quantity: Optional[int] = None,
    qualified_quantity: Optional[int] = None,
    repaired_quantity: Optional[int] = None,
    rejected_quantity: Optional[int] = None,
    actual_start_date: Optional[str] = None,
    actual_end_date: Optional[str] = None,
    process_code: Optional[str] = None,
    process_name: Optional[str] = None,
    process_version: Optional[str] = None,
    unit: Optional[str] = None,
    unit_code: Optional[str] = None,
    production_order_type: Optional[str] = None,
    reporting_type: Optional[str] = None,
    reporting_method: Optional[str] = None,
    is_team_task: Optional[int] = None,
    defect_handling_type: Optional[str] = None,
    rework_type: Optional[str] = None,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取排产数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if work_order_code is not None: payload["workOrderCode"] = work_order_code
    if production_order_code is not None: payload["productionOrderCode"] = production_order_code
    if product_code is not None: payload["productCode"] = product_code
    if product_name is not None: payload["productName"] = product_name
    if workshop_code is not None: payload["workshopCode"] = workshop_code
    if production_line_code is not None: payload["productionLineCode"] = production_line_code
    if planned_start_date is not None: payload["plannedStartDate"] = planned_start_date
    if planned_end_date is not None: payload["plannedEndDate"] = planned_end_date
    if planned_quantity is not None: payload["plannedQuantity"] = planned_quantity
    if work_order_status is not None: payload["workOrderStatus"] = work_order_status
    if actual_quantity is not None: payload["actualQuantity"] = actual_quantity
    if qualified_quantity is not None: payload["qualifiedQuantity"] = qualified_quantity
    if repaired_quantity is not None: payload["repairedQuantity"] = repaired_quantity
    if rejected_quantity is not None: payload["rejectedQuantity"] = rejected_quantity
    if actual_start_date is not None: payload["actualStartDate"] = actual_start_date
    if actual_end_date is not None: payload["actualEndDate"] = actual_end_date
    if process_code is not None: payload["processCode"] = process_code
    if process_name is not None: payload["processName"] = process_name
    if process_version is not None: payload["processVersion"] = process_version
    if unit is not None: payload["unit"] = unit
    if unit_code is not None: payload["unitCode"] = unit_code
    if production_order_type is not None: payload["productionOrderType"] = production_order_type
    if reporting_type is not None: payload["reportingType"] = reporting_type
    if reporting_method is not None: payload["reportingMethod"] = reporting_method
    if is_team_task is not None: payload["isTeamTask"] = is_team_task
    if defect_handling_type is not None: payload["defectHandlingType"] = defect_handling_type
    if rework_type is not None: payload["reworkType"] = rework_type
    if created_by is not None: payload["createdBy"] = created_by
    if created_by_name is not None: payload["createdByName"] = created_by_name
    if updated_by is not None: payload["updatedBy"] = updated_by
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataSchedulingData/queryByPage", data=payload)
    return str(result)

# --- Business Data - Production Data ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_production(
    production_order_code: str,
    product_code: str,
    product_name: str,
    workshop: str,
    production_line: str,
    planned_start_date: str,
    planned_end_date: str,
    super_id: int,
    id: Optional[int] = None,
    planned_quantity: Optional[int] = None,
    actual_start_date: Optional[str] = None,
    actual_end_date: Optional[str] = None,
    qualified_quantity: Optional[int] = None,
    rejected_quantity: Optional[int] = None,
    unit: Optional[str] = None,
    unit_code: Optional[str] = None,
    order_type: Optional[str] = None,
    customer_name: Optional[str] = None,
    order_status: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑生产数据。
    """
    payload = {
        "productionOrderCode": production_order_code,
        "productCode": product_code,
        "productName": product_name,
        "workshop": workshop,
        "productionLine": production_line,
        "plannedStartDate": planned_start_date,
        "plannedEndDate": planned_end_date,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if planned_quantity is not None: payload["plannedQuantity"] = planned_quantity
    if actual_start_date is not None: payload["actualStartDate"] = actual_start_date
    if actual_end_date is not None: payload["actualEndDate"] = actual_end_date
    if qualified_quantity is not None: payload["qualifiedQuantity"] = qualified_quantity
    if rejected_quantity is not None: payload["rejectedQuantity"] = rejected_quantity
    if unit is not None: payload["unit"] = unit
    if unit_code is not None: payload["unitCode"] = unit_code
    if order_type is not None: payload["orderType"] = order_type
    if customer_name is not None: payload["customerName"] = customer_name
    if order_status is not None: payload["orderStatus"] = order_status
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataProductionData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_production_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    production_order_code: Optional[str] = None,
    product_code: Optional[str] = None,
    product_name: Optional[str] = None,
    workshop: Optional[str] = None,
    production_line: Optional[str] = None,
    planned_quantity: Optional[int] = None,
    planned_start_date: Optional[str] = None,
    planned_end_date: Optional[str] = None,
    actual_start_date: Optional[str] = None,
    actual_end_date: Optional[str] = None,
    qualified_quantity: Optional[int] = None,
    rejected_quantity: Optional[int] = None,
    unit: Optional[str] = None,
    unit_code: Optional[str] = None,
    order_type: Optional[str] = None,
    customer_name: Optional[str] = None,
    order_status: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取生产数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if production_order_code is not None: payload["productionOrderCode"] = production_order_code
    if product_code is not None: payload["productCode"] = product_code
    if product_name is not None: payload["productName"] = product_name
    if workshop is not None: payload["workshop"] = workshop
    if production_line is not None: payload["productionLine"] = production_line
    if planned_quantity is not None: payload["plannedQuantity"] = planned_quantity
    if planned_start_date is not None: payload["plannedStartDate"] = planned_start_date
    if planned_end_date is not None: payload["plannedEndDate"] = planned_end_date
    if actual_start_date is not None: payload["actualStartDate"] = actual_start_date
    if actual_end_date is not None: payload["actualEndDate"] = actual_end_date
    if qualified_quantity is not None: payload["qualifiedQuantity"] = qualified_quantity
    if rejected_quantity is not None: payload["rejectedQuantity"] = rejected_quantity
    if unit is not None: payload["unit"] = unit
    if unit_code is not None: payload["unitCode"] = unit_code
    if order_type is not None: payload["orderType"] = order_type
    if customer_name is not None: payload["customerName"] = customer_name
    if order_status is not None: payload["orderStatus"] = order_status
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataProductionData/queryByPage", data=payload)
    return str(result)

# --- Business Data - Order Data ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_order(
    product_code: str,
    product_name: str,
    order_status: str,
    order_date: str,
    required_date: str,
    super_id: int,
    id: Optional[int] = None,
    order_id: Optional[str] = None,
    order_type: Optional[str] = None,
    completed_date: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑订单数据。
    """
    payload = {
        "productCode": product_code,
        "productName": product_name,
        "orderStatus": order_status,
        "orderDate": order_date,
        "requiredDate": required_date,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if order_id is not None: payload["orderId"] = order_id
    if order_type is not None: payload["orderType"] = order_type
    if completed_date is not None: payload["completedDate"] = completed_date
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataOrderData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_order_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    order_id: Optional[str] = None,
    order_type: Optional[str] = None,
    product_code: Optional[str] = None,
    product_name: Optional[str] = None,
    order_status: Optional[str] = None,
    order_date: Optional[str] = None,
    required_date: Optional[str] = None,
    completed_date: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取订单数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if order_id is not None: payload["orderId"] = order_id
    if order_type is not None: payload["orderType"] = order_type
    if product_code is not None: payload["productCode"] = product_code
    if product_name is not None: payload["productName"] = product_name
    if order_status is not None: payload["orderStatus"] = order_status
    if order_date is not None: payload["orderDate"] = order_date
    if required_date is not None: payload["requiredDate"] = required_date
    if completed_date is not None: payload["completedDate"] = completed_date
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataOrderData/queryByPage", data=payload)
    return str(result)

# --- Business Data - Inventory Data ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_inventory(
    material_code: str,
    material_name: str,
    warehouse_code: str,
    warehouse_name: str,
    receipt_date: str,
    super_id: int,
    id: Optional[int] = None,
    total_quantity: Optional[str] = None,
    available_quantity: Optional[str] = None,
    allocated_quantity: Optional[str] = None,
    frozen_quantity: Optional[str] = None,
    transit_quantity: Optional[str] = None,
    unit: Optional[str] = None,
    storage_area: Optional[str] = None,
    location_code: Optional[str] = None,
    barcode: Optional[str] = None,
    batch_number: Optional[str] = None,
    box_code: Optional[str] = None,
    version: Optional[str] = None,
    inventory_age_days: Optional[int] = None,
    production_date: Optional[str] = None,
    owner: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    min_count: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑库存数据。
    """
    payload = {
        "materialCode": material_code,
        "materialName": material_name,
        "warehouseCode": warehouse_code,
        "warehouseName": warehouse_name,
        "receiptDate": receipt_date,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if total_quantity is not None: payload["totalQuantity"] = total_quantity
    if available_quantity is not None: payload["availableQuantity"] = available_quantity
    if allocated_quantity is not None: payload["allocatedQuantity"] = allocated_quantity
    if frozen_quantity is not None: payload["frozenQuantity"] = frozen_quantity
    if transit_quantity is not None: payload["transitQuantity"] = transit_quantity
    if unit is not None: payload["unit"] = unit
    if storage_area is not None: payload["storageArea"] = storage_area
    if location_code is not None: payload["locationCode"] = location_code
    if barcode is not None: payload["barcode"] = barcode
    if batch_number is not None: payload["batchNumber"] = batch_number
    if box_code is not None: payload["boxCode"] = box_code
    if version is not None: payload["version"] = version
    if inventory_age_days is not None: payload["inventoryAgeDays"] = inventory_age_days
    if production_date is not None: payload["productionDate"] = production_date
    if owner is not None: payload["owner"] = owner
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if min_count is not None: payload["minCount"] = min_count
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataInventoryData/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_inventory_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    material_code: Optional[str] = None,
    material_name: Optional[str] = None,
    total_quantity: Optional[str] = None,
    available_quantity: Optional[str] = None,
    allocated_quantity: Optional[str] = None,
    frozen_quantity: Optional[str] = None,
    transit_quantity: Optional[str] = None,
    unit: Optional[str] = None,
    warehouse_code: Optional[str] = None,
    warehouse_name: Optional[str] = None,
    storage_area: Optional[str] = None,
    location_code: Optional[str] = None,
    barcode: Optional[str] = None,
    batch_number: Optional[str] = None,
    box_code: Optional[str] = None,
    version: Optional[str] = None,
    receipt_date: Optional[str] = None,
    inventory_age_days: Optional[int] = None,
    production_date: Optional[str] = None,
    owner: Optional[str] = None,
    updated_by_name: Optional[str] = None,
    min_count: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取库存数据分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if material_code is not None: payload["materialCode"] = material_code
    if material_name is not None: payload["materialName"] = material_name
    if total_quantity is not None: payload["totalQuantity"] = total_quantity
    if available_quantity is not None: payload["availableQuantity"] = available_quantity
    if allocated_quantity is not None: payload["allocatedQuantity"] = allocated_quantity
    if frozen_quantity is not None: payload["frozenQuantity"] = frozen_quantity
    if transit_quantity is not None: payload["transitQuantity"] = transit_quantity
    if unit is not None: payload["unit"] = unit
    if warehouse_code is not None: payload["warehouseCode"] = warehouse_code
    if warehouse_name is not None: payload["warehouseName"] = warehouse_name
    if storage_area is not None: payload["storageArea"] = storage_area
    if location_code is not None: payload["locationCode"] = location_code
    if barcode is not None: payload["barcode"] = barcode
    if batch_number is not None: payload["batchNumber"] = batch_number
    if box_code is not None: payload["boxCode"] = box_code
    if version is not None: payload["version"] = version
    if receipt_date is not None: payload["receiptDate"] = receipt_date
    if inventory_age_days is not None: payload["inventoryAgeDays"] = inventory_age_days
    if production_date is not None: payload["productionDate"] = production_date
    if owner is not None: payload["owner"] = owner
    if updated_by_name is not None: payload["updatedByName"] = updated_by_name
    if min_count is not None: payload["minCount"] = min_count
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataInventoryData/queryByPage", data=payload)
    return str(result)

# --- Business Data - Equipment Mold Change ---

@mcp.tool()
@ensure_login
async def save_or_update_business_data_equipment_mold_change(
    equipment_code: str,
    equipment_name: str,
    previous_material_code: str,
    previous_material_name: str,
    next_material_code: str,
    next_material_name: str,
    planned_change_time: str,
    super_id: int,
    id: Optional[int] = None,
    planned_production_time: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    新增或编辑设备换模数据。
    """
    payload = {
        "equipmentCode": equipment_code,
        "equipmentName": equipment_name,
        "previousMaterialCode": previous_material_code,
        "previousMaterialName": previous_material_name,
        "nextMaterialCode": next_material_code,
        "nextMaterialName": next_material_name,
        "plannedChangeTime": planned_change_time,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if planned_production_time is not None: payload["plannedProductionTime"] = planned_production_time
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataEquipmentMoldChange/saveOrUpdate", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def query_business_data_equipment_mold_change_by_page(
    super_id: int,
    page: int = 1,
    size: int = 10,
    id: Optional[int] = None,
    equipment_code: Optional[str] = None,
    equipment_name: Optional[str] = None,
    previous_material_code: Optional[str] = None,
    previous_material_name: Optional[str] = None,
    next_material_code: Optional[str] = None,
    next_material_name: Optional[str] = None,
    planned_change_time: Optional[str] = None,
    planned_production_time: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取设备换模分页数据。
    """
    payload = {
        "page": page,
        "size": size,
        "superId": super_id
    }
    if id is not None: payload["id"] = id
    if equipment_code is not None: payload["equipmentCode"] = equipment_code
    if equipment_name is not None: payload["equipmentName"] = equipment_name
    if previous_material_code is not None: payload["previousMaterialCode"] = previous_material_code
    if previous_material_name is not None: payload["previousMaterialName"] = previous_material_name
    if next_material_code is not None: payload["nextMaterialCode"] = next_material_code
    if next_material_name is not None: payload["nextMaterialName"] = next_material_name
    if planned_change_time is not None: payload["plannedChangeTime"] = planned_change_time
    if planned_production_time is not None: payload["plannedProductionTime"] = planned_production_time
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/businessDataEquipmentMoldChange/queryByPage", data=payload)
    return str(result)

# --- Organization Management ---

@mcp.tool()
@ensure_login
async def update_company(
    id: int,
    company_name: str,
    pid: Optional[int] = None,
    pname: Optional[str] = None,
    sort: Optional[int] = None,
    validity_period: Optional[int] = None,
    validity_str: Optional[str] = None,
    validity_time: Optional[str] = None
) -> str:
    """
    编辑组织。
    """
    payload = {
        "id": id,
        "companyName": company_name
    }
    if pid is not None: payload["pid"] = pid
    if pname is not None: payload["pname"] = pname
    if sort is not None: payload["sort"] = sort
    if validity_period is not None: payload["validityPeriod"] = validity_period
    if validity_str is not None: payload["validityStr"] = validity_str
    if validity_time is not None: payload["validityTime"] = validity_time
    
    result = await SimClient.post("/api/company/updateCompany", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_company_info_page(
    page: int = 1,
    size: int = 10,
    company_name: Optional[str] = None,
    company_id: Optional[int] = None
) -> str:
    """
    获取组织列表分页。
    """
    payload = {
        "page": page,
        "size": size
    }
    if company_name is not None: payload["companyName"] = company_name
    if company_id is not None: payload["companyId"] = company_id
    
    result = await SimClient.post("/api/company/getCompanyInfoPage", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def create_company(
    company_name: str,
    pid: Optional[int] = None,
    pname: Optional[str] = None,
    sort: Optional[int] = None,
    iot_server_url: Optional[str] = None,
    iot_username: Optional[str] = None,
    iot_password: Optional[str] = None,
    validity_period: Optional[int] = None,
    validity_str: Optional[str] = None,
    validity_time: Optional[str] = None
) -> str:
    """
    新增组织。
    """
    payload = {
        "companyName": company_name
    }
    if pid is not None: payload["pid"] = pid
    if pname is not None: payload["pname"] = pname
    if sort is not None: payload["sort"] = sort
    if iot_server_url is not None: payload["iotServerUrl"] = iot_server_url
    if iot_username is not None: payload["iotUsername"] = iot_username
    if iot_password is not None: payload["iotPassword"] = iot_password
    if validity_period is not None: payload["validityPeriod"] = validity_period
    if validity_str is not None: payload["validityStr"] = validity_str
    if validity_time is not None: payload["validityTime"] = validity_time
    
    result = await SimClient.post("/api/company/createCompany", data=payload)
    return str(result)

@mcp.tool()
@ensure_login
async def get_company_stats_count() -> str:
    """
    获取组织统计信息。
    """
    result = await SimClient.get("/api/company/getCompanyStatsCount")
    return str(result)

@mcp.tool()
@ensure_login
async def get_company_list() -> str:
    """
    获取组织列表下拉框。
    """
    result = await SimClient.get("/api/company/getCompanyList")
    return str(result)

# --- Permission Management ---

@mcp.tool()
@ensure_login
async def get_menu_permissions() -> str:
    """
    获取用户拥有菜单权限。
    """
    result = await SimClient.get("/api/permission/getMenuPermissions")
    return str(result)

@mcp.tool()
@ensure_login
async def get_menu_authorization() -> str:
    """
    获取菜单授权列表。
    """
    result = await SimClient.get("/api/permission/getMenuAuthorization")
    return str(result)
