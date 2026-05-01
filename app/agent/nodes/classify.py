from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from typing import Literal

from app.agent.state import AgentState
from app.config import settings

SYSTEM_PROMPT = """Você é um classificador de intenções para um chatbot de clínica de exames.

Classifique a última mensagem do paciente em uma das categorias:
- faq: dúvidas gerais (horário, endereço, preparo de exames, convênios, valores)
- agendamento: deseja marcar, remarcar ou cancelar um exame
- resultado: pergunta sobre resultado de exame já realizado
- humano: quer falar com um atendente humano
- outro: fora do escopo

Responda apenas com a categoria, sem explicação."""


class IntentOutput(BaseModel):
    intent: Literal["faq", "agendamento", "resultado", "humano", "outro"]


async def classify_intent(state: AgentState) -> dict:
    llm = ChatAnthropic(
        model=settings.model_name,
        api_key=settings.anthropic_api_key,
    ).with_structured_output(IntentOutput)

    result = await llm.ainvoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
    return {"intent": result.intent}


def route_by_intent(state: AgentState) -> str:
    return state.get("intent", "outro")
