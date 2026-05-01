from langchain_core.messages import AIMessage

from app.agent.state import AgentState

HANDOFF_MESSAGE = (
    "Entendido! Vou transferir você para um de nossos atendentes. "
    "Por favor, aguarde um momento — em breve alguém entrará em contato por aqui. "
    "Nosso horário de atendimento é seg-sex das 07h às 17h e sáb das 07h às 12h."
)


async def handle_handoff(state: AgentState) -> dict:
    return {"messages": [AIMessage(content=HANDOFF_MESSAGE)]}
