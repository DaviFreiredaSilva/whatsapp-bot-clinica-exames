"""
Smoke test para verificar a conexão com a Evolution API.

Uso:
    python scripts/test_evolution.py <numero_destino>

Exemplo:
    python scripts/test_evolution.py 5511999999999

O número deve estar no formato internacional sem '+' (DDI + DDD + número).
"""

import asyncio
import sys
import httpx
from app.config import settings


async def check_instance() -> bool:
    """Verifica se a instância está conectada ao WhatsApp."""
    url = f"{settings.evolution_api_url}/instance/fetchInstances"
    headers = {"apikey": settings.evolution_api_key}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        instances = response.json()

    target = next(
        (i for i in instances if i.get("instance", {}).get("instanceName") == settings.evolution_instance),
        None,
    )
    if not target:
        print(f"[ERRO] Instância '{settings.evolution_instance}' não encontrada.")
        print(f"       Instâncias disponíveis: {[i.get('instance', {}).get('instanceName') for i in instances]}")
        return False

    state = target.get("instance", {}).get("state", "unknown")
    print(f"[OK] Instância '{settings.evolution_instance}' encontrada — estado: {state}")
    return state == "open"


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    phone = sys.argv[1]

    print(f"\nEvolution API URL : {settings.evolution_api_url}")
    print(f"Instância         : {settings.evolution_instance}")
    print(f"Destino           : {phone}\n")

    # 1. Verifica instância
    print("1. Verificando instância...")
    connected = await check_instance()
    if not connected:
        print("[AVISO] Instância não está com estado 'open'. Tente mesmo assim? (s/N) ", end="")
        if input().strip().lower() != "s":
            sys.exit(1)

    # 2. Envia mensagem de teste
    print("\n2. Enviando mensagem de teste...")
    from app.services.evolution import send_text
    await send_text(phone, "🤖 Teste de integração OK! Bot da clínica conectado.")
    print(f"[OK] Mensagem enviada para {phone}.")


if __name__ == "__main__":
    asyncio.run(main())
