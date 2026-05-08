import httpx
from app.config import settings

_BASE = "https://api.z-api.io/instances/{instance_id}/token/{token}"


async def send_text(phone: str, text: str) -> None:
    url = _BASE.format(
        instance_id=settings.zapi_instance_id,
        token=settings.zapi_token,
    ) + "/send-text"
    headers = {"Client-Token": settings.zapi_client_token}
    payload = {"phone": phone, "message": text}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
