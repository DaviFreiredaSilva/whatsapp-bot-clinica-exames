import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_webhook_unauthorized():
    response = client.post(
        "/webhook/message",
        json={"phone": "5511999999999", "message": "oi"},
        headers={"x-api-secret": "wrong-secret"},
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

    with patch("app.api.webhook.get_graph") as mock_get_graph:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_result
        mock_get_graph.return_value = mock_graph

        response = client.post(
            "/webhook/message",
            json={"phone": "5511999999999", "message": "oi"},
            headers={"x-api-secret": "dev-secret"},
        )

    assert response.status_code == 200
    assert response.json()["phone"] == "5511999999999"
    assert "response" in response.json()
