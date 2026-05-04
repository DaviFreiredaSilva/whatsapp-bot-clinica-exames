import hashlib
import hmac

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.agent.graph import get_graph
from app.config import settings
from app.services.whatsapp import send_text

router = APIRouter()


@router.get("/webhook/message")
async def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_webhook_verify_token:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/webhook/message")
async def receive_message(request: Request):
    body = await request.body()

    if settings.meta_app_secret:
        signature = request.headers.get("x-hub-signature-256", "")
        expected = "sha256=" + hmac.new(
            settings.meta_app_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") != "text":
                    continue

                phone = msg["from"]
                text = msg["text"]["body"]

                graph = get_graph()
                config = {"configurable": {"thread_id": phone}}
                result = await graph.ainvoke(
                    {"messages": [{"role": "user", "content": text}], "phone": phone, "intent": None},
                    config=config,
                )
                last = result["messages"][-1]
                await send_text(phone, last.content)

    return {"status": "ok"}
