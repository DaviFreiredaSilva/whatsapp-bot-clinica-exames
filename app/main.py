from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.agent.graph import close_graph, init_graph
from app.api.chat import router as chat_router
from app.api.webhook import router
from app.rag.vectorstore import init_rag
from app.services.appointments import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_rag()
    await init_graph()
    yield
    await close_graph()


app = FastAPI(
    title="WhatsApp Bot — Clínica de Exames",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
