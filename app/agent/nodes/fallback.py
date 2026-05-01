from langchain_core.messages import AIMessage

from app.agent.state import AgentState

FALLBACK_MESSAGE = (
    "Olá! Sou o assistente virtual da clínica. Posso ajudar com:\n\n"
    "• *Agendamentos* — marcar, remarcar ou cancelar exames\n"
    "• *Dúvidas gerais* — horários, endereço, convênios, preparo para exames\n"
    "• *Resultados* — como acessar seus resultados\n"
    "• *Atendente humano* — transferir para nossa equipe\n\n"
    "Como posso te ajudar?"
)


async def handle_fallback(state: AgentState) -> dict:
    return {"messages": [AIMessage(content=FALLBACK_MESSAGE)]}
