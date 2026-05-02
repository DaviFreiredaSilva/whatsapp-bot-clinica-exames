from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.agent.graph import init_graph, close_graph
from app.api.webhook import router
from app.rag.vectorstore import init_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/health")
async def health():
    return {"status": "ok"}
