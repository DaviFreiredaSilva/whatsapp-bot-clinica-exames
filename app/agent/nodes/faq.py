from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.config import settings
from app.rag.vectorstore import get_retriever

BASE_PROMPT = """Você é um assistente virtual cordial de uma clínica de exames laboratoriais.
Responda dúvidas dos pacientes sobre horários, endereço, convênios, preparo para exames, valores e formas de pagamento.
Seja objetivo e cordial. Se não souber a informação específica da clínica, oriente o paciente a ligar ou visitar a unidade.
Nunca invente dados médicos ou resultados.
Responda sempre em português brasileiro."""


async def handle_faq(state: AgentState) -> dict:
    llm = ChatOpenAI(model=settings.model_name, api_key=settings.openai_api_key)

    system_prompt = BASE_PROMPT
    retriever = get_retriever()

    if retriever:
        last_message = state["messages"][-1].content
        docs = await retriever.ainvoke(last_message)
        if docs:
            context = "\n\n".join(doc.page_content for doc in docs)
            system_prompt = f"{BASE_PROMPT}\n\nInformações da clínica:\n{context}"

    response = await llm.ainvoke([SystemMessage(content=system_prompt), *state["messages"]])
    return {"messages": [response]}
