from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.agent.state import AgentState
from app.agent.nodes.classify import classify_intent, route_by_intent
from app.agent.nodes.faq import handle_faq
from app.agent.nodes.scheduling import handle_scheduling
from app.agent.nodes.resultado import handle_resultado
from app.agent.nodes.handoff import handle_handoff
from app.agent.nodes.fallback import handle_fallback
from app.config import settings

_graph = None
_pool = None


async def init_graph():
    global _graph, _pool

    _pool = AsyncConnectionPool(conninfo=settings.database_url, open=False)
    await _pool.open()

    checkpointer = AsyncPostgresSaver(_pool)
    await checkpointer.setup()

    builder = StateGraph(AgentState)

    builder.add_node("classify", classify_intent)
    builder.add_node("faq", handle_faq)
    builder.add_node("agendamento", handle_scheduling)
    builder.add_node("resultado", handle_resultado)
    builder.add_node("humano", handle_handoff)
    builder.add_node("outro", handle_fallback)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "faq": "faq",
            "agendamento": "agendamento",
            "resultado": "resultado",
            "humano": "humano",
            "outro": "outro",
        },
    )
    builder.add_edge("faq", END)
    builder.add_edge("agendamento", END)
    builder.add_edge("resultado", END)
    builder.add_edge("humano", END)
    builder.add_edge("outro", END)

    _graph = builder.compile(checkpointer=checkpointer)


async def close_graph():
    if _pool:
        await _pool.close()


def get_graph():
    if _graph is None:
        raise RuntimeError("Graph not initialized. Call init_graph() first.")
    return _graph
