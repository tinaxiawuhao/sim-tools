import httpx
from typing import Optional, Dict, Any

class SimClient:
    BASE_URL = "https://dt-fflc-vanlinks.hdt.cosmoplat.com"
    _token: Optional[str] = None
    _headers: Dict[str, str] = {
        "Content-Type": "application/json"
    }

    @classmethod
    def set_token(cls, token: str):
        cls._token = token
        # Assuming Bearer token, adjust if needed based on real API response
        cls._headers["Authorization"] = f"{token}" 

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._token is not None

    @classmethod
    async def login(cls, username: str, password: str) -> str:
        url = f"{cls.BASE_URL}/api/login"
        payload = {
            "username": username,
            "password": password,
            "computerMachineCode": "mcp-server-001",
            "clientCategory": "WEB"
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10.0)
                resp.raise_for_status()
                result = resp.json()
                
                # Check for success code (Doc says 1 is success, but example shows 0. We'll accept 1 or 0 if msg is empty/success)
                code = result.get("code")
                # Assuming success if code is 1 (per doc text) or if it contains a token
                
                data = result.get("data", {})
                token = None
                
                # Try to find token in data
                if isinstance(data, dict):
                    token = data.get("token") or data.get("access_token")
                
                # Try headers if not in data
                if not token:
                    token = resp.headers.get("Authorization")
                
                # If we found a token, save it
                if token:
                    cls.set_token(token)
                    return f"Login successful. Token stored."
                
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
    async def post(cls, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=cls._headers, timeout=30.0)
            # resp.raise_for_status() # Let's return the JSON even on error to see msg
            return resp.json()

    @classmethod
    async def get(cls, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=cls._headers, timeout=30.0)
            return resp.json()

    @classmethod
    async def delete(cls, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not cls.is_logged_in():
             return {"code": -1, "msg": "Not logged in. Please call 'login' tool first."}
        
        url = f"{cls.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, params=params, headers=cls._headers, timeout=30.0)
            return resp.json()
