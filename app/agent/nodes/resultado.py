from langchain_core.messages import AIMessage

from app.agent.state import AgentState

RESULT_MESSAGE = (
    "Para consultar seu resultado de exame, você pode acessar nosso portal online "
    "em [link do portal] com seu CPF, ou comparecer à unidade com documento de identidade. "
    "Resultados de exames de imagem ficam prontos em até 2 dias úteis; "
    "exames laboratoriais geralmente ficam prontos no mesmo dia ou em até 24 horas.\n\n"
    "Caso precise de ajuda adicional, posso transferir você para um atendente."
)


async def handle_resultado(state: AgentState) -> dict:
    return {"messages": [AIMessage(content=RESULT_MESSAGE)]}
