import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_unauthorized():
    response = client.post(
        "/webhook/message",
        json={"phone": "5511999999999", "message": "oi"},
        headers={"x-api-secret": "wrong-secret-xyz"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_returns_response():
    mock_result = {
        "messages": [
            type("Msg", (), {"content": "Olá! Como posso ajudar?"})()
        ],
        "phone": "5511999999999",
        "intent": "outro",
    }

    with patch("app.api.webhook.get_graph") as mock_get_graph, \
         patch("app.api.webhook.send_text", new_callable=AsyncMock) as mock_send:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_result
        mock_get_graph.return_value = mock_graph

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/webhook/message",
                json={"phone": "5511999999999", "message": "oi"},
                headers={"x-api-secret": settings.api_secret},
            )

        mock_send.assert_awaited_once_with("5511999999999", "Olá! Como posso ajudar?")

    assert response.status_code == 200
    assert response.json()["phone"] == "5511999999999"
    assert "response" in response.json()
