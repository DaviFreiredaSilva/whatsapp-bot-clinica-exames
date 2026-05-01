from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.config import settings

SYSTEM_PROMPT = """Você é um assistente virtual cordial de uma clínica de exames laboratoriais.
Responda dúvidas dos pacientes sobre:
- Horários de funcionamento (ex.: seg-sex 07h-17h, sáb 07h-12h)
- Endereço e como chegar
- Convênios aceitos
- Preparo para exames (jejum, restrições, etc.)
- Valores e formas de pagamento

Seja objetivo e cordial. Se não souber a informação específica da clínica, oriente o paciente
a ligar ou visitar a unidade. Nunca invente dados médicos ou resultados.
Responda sempre em português brasileiro."""


async def handle_faq(state: AgentState) -> dict:
    llm = ChatAnthropic(
        model=settings.model_name,
        api_key=settings.anthropic_api_key,
    )
    response = await llm.ainvoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
    return {"messages": [response]}
