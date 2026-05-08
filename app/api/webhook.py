import logging

from fastapi import APIRouter, HTTPException, Request

from app.agent.graph import get_graph
from app.config import settings
from app.services.whatsapp import send_text

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook/zapi")
async def zapi_webhook(request: Request):
    # Valida o Client-Token se configurado
    if settings.zapi_client_token:
        token = request.headers.get("client-token", "")
        if token != settings.zapi_client_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()

    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        return {"status": "ignored"}

    # Só processa texto
    text_obj = data.get("text")
    if not text_obj:
        return {"status": "ignored"}

    text = text_obj.get("message", "").strip()
    if not text:
        return {"status": "ignored"}

    # Remove sufixo @c.us ou @g.us que o Z-API pode enviar
    phone = data.get("phone", "").split("@")[0]
    if not phone:
        return {"status": "ignored"}

    logger.info("Mensagem recebida de %s: %s", phone, text)

    try:
        graph = get_graph()
        config = {"configurable": {"thread_id": phone}}
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": text}], "phone": phone, "intent": None},
            config=config,
        )
        last = result["messages"][-1]
        logger.info("Resposta gerada: %s", last.content)
        await send_text(phone, last.content)
    except Exception as e:
        logger.error("Erro ao processar mensagem de %s: %s", phone, e, exc_info=True)

    return {"status": "ok"}
