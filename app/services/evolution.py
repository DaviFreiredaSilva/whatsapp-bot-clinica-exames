import httpx
from app.config import settings


async def send_text(phone: str, text: str) -> None:
    """Envia mensagem de texto via Evolution API (uso para mensagens proativas)."""
    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}"
    headers = {"apikey": settings.evolution_api_key}
    payload = {"number": phone, "text": text}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
