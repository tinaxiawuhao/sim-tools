import httpx
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

import logging
import json
import os

# 配置日志
logger = logging.getLogger("SimClient")

# Token 文件路径
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")

# 使用全局变量存储 token 和 headers，确保在不同请求之间保持状态
_global_token: Optional[str] = None
_global_headers: Dict[str, str] = {
    "Content-Type": "application/json"
}

class SimClient:
    BASE_URL = os.getenv("BASE_URL", "https://dt-fflc-vanlinks.hdt.cosmoplat.com")

    @classmethod
    def _load_token(cls):
        """从文件加载 token"""
        global _global_token
        global _global_headers
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                    token = data.get("token")
                    if token:
                        _global_token = token
                        # 添加 "Bearer " 前缀，符合标准 Authorization 请求头格式
                        _global_headers["Authorization"] = f"Bearer {token}"
                        logger.info(f"Token loaded from file: {token[:20]}...")
                        logger.info(f"Authorization header set to: Bearer {token[:20]}...")
        except Exception as e:
            logger.error(f"Error loading token from file: {e}")

    @classmethod
    def _save_token(cls, token: str):
        """将 token 保存到文件"""
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": token}, f)
            logger.info(f"Token saved to file: {token[:20]}...")
        except Exception as e:
            logger.error(f"Error saving token to file: {e}")

    @classmethod
    def set_token(cls, token: str):
        global _global_token
        global _global_headers
        logger.info(f"Setting token: {token[:20]}...")  # 只记录前 20 个字符，保护隐私
        
        # 检查 token 是否已经包含 "Bearer " 前缀
        if token.startswith("Bearer "):
            # 如果已经包含 "Bearer " 前缀，就直接使用
            _global_token = token
            _global_headers["Authorization"] = token
        else:
            # 如果没有包含 "Bearer " 前缀，就添加
            _global_token = token
            _global_headers["Authorization"] = f"Bearer {token}"
        
        cls._save_token(token)  # 保存到文件
        logger.info(f"Token set successfully. Current token: {_global_token[:20]}...")
        logger.info(f"Authorization header set to: {_global_headers['Authorization']}")

    @classmethod
    def is_logged_in(cls) -> bool:
        global _global_token
        # 尝试从文件加载 token
        if _global_token is None:
            cls._load_token()
        status = _global_token is not None
        logger.info(f"Checking login status: {status}")
        if status:
            logger.info(f"Current token: {_global_token[:20]}...")
        return status

    @classmethod
    async def login(cls, username: str, password: str) -> str:
        
        url = f"{cls.BASE_URL}/api/login"
        payload = {
            "username": username,
            "password": password,
            "computerMachineCode": "mcp-server-001",
            "clientCategory": "WEB"
        }
        logger.info(f"POST request to: {url}")
        logger.info(f"POST data: {payload}")
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10.0)
                logger.info(f"POST response status: {resp.status_code}")
                logger.info(f"POST response headers: {resp.headers}")
                result = resp.json()
                logger.info(f"POST response body: {result}")
                
                # Check for success code
                code = result.get("code")
                
                # Check if login failed
                if code != 1:
                    # Login failed
                    msg = result.get("msg", "Login failed")
                    logger.error(f"Login failed: {code} - {msg}")
                    return f"Login failed: {msg}"
                
                # Login successful, get token from data
                data = result.get("data", {})
                token = None
                
                # Directly use data as token if it's a string
                if isinstance(data, str):
                    token = data
                    logger.info(f"Found token in data: {token[:20]}...")
                
                # Try headers if not in data
                if not token:
                    token = resp.headers.get("Authorization")
                    logger.info(f"Found token in headers: {token[:20]}...")
                
                # If we found a token, save it
                if token:
                    cls.set_token(token)
                    return f"Login successful. Token stored."
                else:
                    logger.error(f"No token found in response: {result}")
                    return f"Login successful but no token found."
                
                # If no token found but code indicates success, maybe it's cookie based?
                # But MCP server is stateless-ish, we need a token for subsequent requests usually.
                # For now, let's assume if code is 1, we are good? But we need a token for headers.
                # If the API relies on Cookies, httpx client session needs to be persistent.
                # We are creating a new client every time.
                # Let's check Set-Cookie headers.
                cookies = resp.cookies
                if cookies:
                    # We might need to store cookies. 
                    # For simplicity, let's assume token based first. 
                    # If we fail, we might need to refactor to use a persistent session.
                    pass

                return f"Login response received: {result}. No explicit token found."

        except Exception as e:
            return f"Login failed: {str(e)}"
        


    @classmethod
    async def get(cls, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        global _global_headers
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        logger.info(f"GET request to: {url}")
        logger.info(f"GET params: {params}")
        logger.info(f"GET headers: {_global_headers}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=_global_headers, timeout=30.0)
            logger.info(f"GET response status: {resp.status_code}")
            return resp.json()

    @classmethod
    async def post(cls, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        global _global_headers
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        logger.info(f"POST request to: {url}")
        logger.info(f"POST data: {data}")
        logger.info(f"POST headers: {_global_headers}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=_global_headers, timeout=30.0)
            logger.info(f"POST response status: {resp.status_code}")
            return resp.json()

    @classmethod
    async def put(cls, path: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        global _global_headers
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        logger.info(f"PUT request to: {url}")
        logger.info(f"PUT data: {data}")
        logger.info(f"PUT params: {params}")
        logger.info(f"PUT headers: {_global_headers}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.put(url, json=data, params=params, headers=_global_headers, timeout=30.0)
            logger.info(f"PUT response status: {resp.status_code}")
            return resp.json()

    @classmethod
    async def delete(cls, path: str, params: Dict[str, Any] = None, data: Any = None) -> Dict[str, Any]:
        global _global_headers
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        logger.info(f"DELETE request to: {url}")
        logger.info(f"DELETE data: {data}")
        logger.info(f"DELETE params: {params}")
        logger.info(f"DELETE headers: {_global_headers}")
        
        async with httpx.AsyncClient() as client:
            if data is not None:
                resp = await client.request("DELETE", url, params=params, json=data, headers=_global_headers, timeout=30.0)
            else:
                resp = await client.delete(url, params=params, headers=_global_headers, timeout=30.0)
            logger.info(f"DELETE response status: {resp.status_code}")
            return resp.json()
