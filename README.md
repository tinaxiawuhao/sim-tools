# Sim MCP Tools

这是一个基于 Model Context Protocol (MCP) 的服务器实现，旨在将仿真平台（dt-commercialization）的核心业务能力暴露给 AI 助手（如 Claude Desktop, Cursor, Trae 等）。

本项目采用 **SSE (Server-Sent Events)** 模式运行，支持通过 HTTP 协议进行工具发现和调用，并内置了基于 Token 的身份验证机制。

## ✨ 功能特性

*   **SSE 传输支持**：基于 Starlette 和 `mcp.server.sse` 实现，兼容标准 MCP 客户端。
*   **自动鉴权管理**：
    *   提供 `login` 工具获取访问令牌。
    *   所有受保护的工具通过 `@ensure_login` 装饰器自动拦截未登录请求。
    *   全局单例 `SimClient` 管理 Token 状态。
*   **丰富的业务能力**：已集成案例管理、用户查询、模型点位配置等核心接口。
*   **类型安全**：使用 Pydantic 模型和 Python 类型注解，提供清晰的工具定义。

## 🛠️ 技术栈

*   **Python 3.12+**
*   **uv**: 现代 Python 包和项目管理器。
*   **mcp**: 官方 Python SDK。
*   **FastAPI / Starlette**: Web 服务框架。
*   **httpx**: 异步 HTTP 客户端。

## 🚀 快速开始

### 1. 环境准备

确保已安装 [uv](https://github.com/astral-sh/uv)。

```bash
# 克隆项目（假设已在项目目录）
cd sim-mcp-tools

# 初始化环境并安装依赖
uv sync
```

### 2. 启动服务

使用 `uv` 运行服务器脚本：

```bash
# 默认端口 80
uv run server.py

# 指定端口
uv run server.py --port 80
```

启动成功后，控制台将输出：
```text
Starting SSE server on http://0.0.0.0:80
Tools available at http://0.0.0.0:80/mcp/tools
```

### 3. 配置 MCP 客户端

在您的 MCP 客户端（如 Claude Desktop 配置文件 `claude_desktop_config.json`）中添加以下配置：

```json
{
  "mcpServers": {
    "sim-tools": {
      "command": "uv",
      "args": [
        "run",
        "server.py",
        "--port",
        "80"
      ],
      "cwd": "D:/study/sim-mcp-tools",
      "env": {}
    }
  }
}
```
*注意：由于本项目是 SSE Server，上述配置是让客户端自动启动 Server。如果 Server 已经在后台运行，某些客户端支持直接连接 SSE URL (`http://localhost:80/sse`)。*

## 🧰 可用工具 (Tools)

### 身份认证
*   **`login(username, password)`**: 登录仿真平台。**这是必须调用的第一个工具**。

### 案例管理
*   **`query_cases_list(case_name, page_index, page_size)`**: 分页查询案例列表。
*   **`get_case_details(case_id)`**: 获取指定案例详情。
*   **`delete_case(case_id)`**: 删除案例。

### 用户与角色管理
*   **`get_user_list(login_name)`**: 查询用户列表。
*   **`get_role_list(role_name, role_type, page, size)`**: 查询角色列表。

### 价值流与模板
*   **`query_value_stream_templates(template_name, case_id)`**: 查询价值流模板列表。
*   **`save_value_stream_template(template_name, template_json, id, case_id)`**: 新增或编辑价值流模板。
*   **`delete_value_stream_template(id)`**: 删除价值流模板。
*   **`get_value_stream_object_data_box_list(case_id, object_type, object_name)`**: 查询价值流对象数据框。
*   **`save_value_stream_object_data_box(...)`**: 新增或编辑价值流对象数据框。
*   **`delete_value_stream_object_data_box(id)`**: 删除价值流对象数据框。

### 模型与点位
*   **`save_case_model_point(...)`**: 新增或更新本地 PLC 调试的模型点位。
*   **`query_case_model_points(case_id, ...)`**: 查询模型点位数据。

## 📂 项目结构

```text
sim-mcp-tools/
├── data/
│   └── sim_interface.md    # 接口定义参考文档
├── skills/
│   ├── __init__.py
│   ├── sim_client.py       # HTTP 客户端封装 (httpx)
│   └── sim_tools.py        # MCP 工具定义与实现
├── server.py               # 服务入口 (Starlette/SSE)
├── pyproject.toml          # 项目配置
└── README.md               # 项目文档
```

## 📝 开发指南

### 添加新工具

1.  **定义接口**: 在 `skills/sim_client.py` 中添加对应的 HTTP 请求方法（如果通用方法 `post/get` 不满足需求）。
2.  **注册工具**: 在 `skills/sim_tools.py` 中使用 `@mcp.tool()` 注册函数。
3.  **添加鉴权**: 加上 `@ensure_login` 装饰器。

示例：

```python
@mcp.tool()
@ensure_login
async def my_new_tool(param: str) -> str:
    """工具描述"""
    result = await SimClient.post("/api/new/path", data={"p": param})
    return str(result)
```

## ⚠️ 注意事项

*   **Token 有效期**：目前的实现将 Token 存储在内存中（`SimClient` 类变量）。重启服务会导致 Token 丢失，需要重新调用 `login` 工具。
*   **API 地址**：默认连接到 `https://dt-fflc-vanlinks.hdt.cosmoplat.com`，可在 `sim_client.py` 中修改 `BASE_URL`。
