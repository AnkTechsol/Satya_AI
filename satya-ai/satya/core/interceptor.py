# Stub for request interceptor middleware
from fastapi import Request, HTTPException
from ..config import settings
from ..utils.hashing import verify_api_key

async def verify_satya_key(request: Request):
    """Dependency to verify the X-Satya-Key header."""
    api_key = request.headers.get("X-Satya-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="X-Satya-Key header missing")

    allowed_keys = [k.strip() for k in settings.satya_agent_keys.split(",")]
    if not verify_api_key(api_key, allowed_keys):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key
