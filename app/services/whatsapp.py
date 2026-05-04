import httpx
from app.config import settings

BASE_URL = "https://graph.facebook.com"


async def send_text(phone: str, text: str) -> None:
    url = f"{BASE_URL}/{settings.meta_api_version}/{settings.meta_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.meta_access_token}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
