from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.agent.graph import get_graph
from app.config import settings

router = APIRouter()


class IncomingMessage(BaseModel):
    phone: str
    message: str
    instance: str = ""


class OutgoingMessage(BaseModel):
    phone: str
    response: str


@router.post("/webhook/message", response_model=OutgoingMessage)
async def receive_message(
    payload: IncomingMessage,
    x_api_secret: str = Header(default=""),
):
    if x_api_secret != settings.api_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    graph = get_graph()
    config = {"configurable": {"thread_id": payload.phone}}

    result = await graph.ainvoke(
        {
            "messages": [{"role": "user", "content": payload.message}],
            "phone": payload.phone,
            "intent": None,
        },
        config=config,
    )

    last_message = result["messages"][-1]
    return OutgoingMessage(phone=payload.phone, response=last_message.content)
