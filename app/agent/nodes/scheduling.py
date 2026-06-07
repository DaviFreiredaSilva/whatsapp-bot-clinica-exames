from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

import app.services.appointments as svc
from app.agent.state import AgentState
from app.config import settings

SYSTEM_PROMPT = """Você é um assistente de agendamento de uma clínica de exames laboratoriais.

Você pode ajudar o paciente a:
- MARCAR um novo exame
- CANCELAR um exame existente
- REMARCAR (mudar a data) de um exame existente

## Fluxo para MARCAR:
1. Pergunte o tipo de exame desejado
2. Use verificar_horarios_disponiveis para mostrar os horários disponíveis
3. Peça que o paciente escolha um horário pelo número
4. Colete o nome completo do paciente
5. Colete o CPF (aceite com ou sem formatação)
6. Mostre um resumo completo e peça confirmação explícita ("sim" ou "confirmo")
7. Somente após confirmação, use agendar_exame para registrar

## Fluxo para CANCELAR:
1. Peça o CPF do paciente
2. Use buscar_agendamentos para mostrar os agendamentos ativos
3. Pergunte qual deseja cancelar (pelo número da lista)
4. Peça confirmação
5. Somente após confirmação, use cancelar_agendamento

## Fluxo para REMARCAR:
1. Peça o CPF do paciente
2. Use buscar_agendamentos para mostrar os agendamentos ativos
3. Pergunte qual deseja remarcar (pelo número da lista)
4. Use verificar_horarios_disponiveis para mostrar os novos horários
5. Peça que o paciente escolha pelo número
6. Mostre resumo da remarcação e peça confirmação
7. Somente após confirmação, use remarcar_agendamento

## Regras:
- NUNCA registre ou altere dados sem confirmação explícita do paciente
- Responda sempre em português brasileiro
- Seja objetivo e cordial
"""


def _build_tools(phone: str):
    @tool
    async def verificar_horarios_disponiveis() -> str:
        """Verifica os horários livres para agendamento nos próximos 7 dias."""
        slots = await svc.get_available_slots()
        if not slots:
            return "Não há horários disponíveis nos próximos 7 dias. Tente ligar para a clínica."
        lines = [f"{i + 1}. {svc.format_slot(dt)} (ID interno: {sid})" for i, (sid, dt) in enumerate(slots)]
        return "Horários disponíveis:\n" + "\n".join(lines)

    @tool
    async def buscar_agendamentos(cpf: str) -> str:
        """Busca os agendamentos ativos de um paciente pelo CPF."""
        rows = await svc.get_appointments_by_cpf(cpf)
        if not rows:
            return "Nenhum agendamento ativo encontrado para esse CPF."
        lines = [
            f"{i + 1}. {row.exam_type} — {svc.format_slot(row.datetime)} (ID interno: {row.id})"
            for i, row in enumerate(rows)
        ]
        return "Agendamentos encontrados:\n" + "\n".join(lines)

    @tool
    async def agendar_exame(nome: str, cpf: str, tipo_exame: str, slot_id: int) -> str:
        """Registra um novo agendamento após confirmação do paciente."""
        try:
            appt = await svc.create_appointment(nome, cpf, phone, tipo_exame, slot_id)
        except ValueError as e:
            return str(e)
        return (
            f"Agendamento registrado com sucesso!\n"
            f"Protocolo: #{appt.id}\n"
            f"Paciente: {appt.patient_name}\n"
            f"Exame: {appt.exam_type}\n"
            f"Em caso de dúvidas, entre em contato com a clínica informando o protocolo."
        )

    @tool
    async def cancelar_agendamento(appointment_id: int) -> str:
        """Cancela um agendamento pelo ID interno. Libera o horário para outros pacientes."""
        success = await svc.cancel_appointment(appointment_id)
        if success:
            return f"Agendamento #{appointment_id} cancelado com sucesso. O horário foi liberado."
        return "Não foi possível cancelar. O agendamento pode já ter sido cancelado ou não existe."

    @tool
    async def remarcar_agendamento(appointment_id: int, novo_slot_id: int) -> str:
        """Remarca um agendamento para um novo horário."""
        appt = await svc.reschedule_appointment(appointment_id, novo_slot_id)
        if appt:
            return (
                f"Agendamento #{appt.id} remarcado com sucesso!\n"
                f"Exame: {appt.exam_type}\n"
                f"Novo protocolo: #{appt.id}"
            )
        return "Não foi possível remarcar. O agendamento pode estar cancelado ou inválido."

    return [
        verificar_horarios_disponiveis,
        buscar_agendamentos,
        agendar_exame,
        cancelar_agendamento,
        remarcar_agendamento,
    ]


async def handle_scheduling(state: AgentState) -> dict:
    phone = state["phone"]
    tools = _build_tools(phone)
    tool_map = {t.name: t for t in tools}

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.google_api_key,
    ).bind_tools(tools)

    accumulated: list = []
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]

    for _ in range(6):
        response = await llm.ainvoke(messages)
        accumulated.append(response)

        if not response.tool_calls:
            break

        tool_results = []
        for call in response.tool_calls:
            result = await tool_map[call["name"]].ainvoke(call["args"])
            tool_results.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )

        accumulated.extend(tool_results)
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"], *accumulated]

    return {"messages": accumulated}
