import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.agent.graph import get_graph

router = APIRouter()
logger = logging.getLogger(__name__)

_DEMO_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Bot Clínica — Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      background: #ece5dd;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* ── Header ── */
    .header {
      background: #075e54;
      color: #fff;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
      box-shadow: 0 1px 3px rgba(0,0,0,.3);
    }
    .avatar {
      width: 42px; height: 42px;
      border-radius: 50%;
      background: #25d366;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      flex-shrink: 0;
    }
    .header-info h2 { font-size: 16px; font-weight: 600; }
    .header-info p  { font-size: 13px; opacity: .75; }

    /* ── Messages ── */
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .bubble {
      max-width: 72%;
      padding: 8px 12px 6px;
      border-radius: 8px;
      font-size: 14.5px;
      line-height: 1.45;
      word-wrap: break-word;
      white-space: pre-wrap;
      box-shadow: 0 1px 1px rgba(0,0,0,.12);
    }
    .bubble .time {
      font-size: 11px;
      opacity: .55;
      margin-top: 3px;
      text-align: right;
    }
    .bot-bubble  { background: #fff;    align-self: flex-start; border-top-left-radius: 2px; }
    .user-bubble { background: #dcf8c6; align-self: flex-end;   border-top-right-radius: 2px; }

    /* ── Typing indicator ── */
    .typing {
      background: #fff;
      align-self: flex-start;
      padding: 10px 14px;
      border-radius: 8px;
      border-top-left-radius: 2px;
      display: flex;
      gap: 4px;
      align-items: center;
      box-shadow: 0 1px 1px rgba(0,0,0,.12);
    }
    .typing span {
      width: 8px; height: 8px;
      background: #90949c;
      border-radius: 50%;
      animation: bounce 1.3s infinite;
    }
    .typing span:nth-child(2) { animation-delay: .2s; }
    .typing span:nth-child(3) { animation-delay: .4s; }
    @keyframes bounce {
      0%, 60%, 100% { transform: translateY(0); }
      30%            { transform: translateY(-6px); }
    }

    /* ── Input bar ── */
    .input-bar {
      background: #f0f0f0;
      padding: 8px 12px;
      display: flex;
      gap: 8px;
      align-items: center;
      flex-shrink: 0;
    }
    .input-bar input {
      flex: 1;
      padding: 10px 16px;
      border: none;
      border-radius: 22px;
      font-size: 15px;
      outline: none;
      background: #fff;
    }
    .input-bar button {
      width: 46px; height: 46px;
      border-radius: 50%;
      border: none;
      background: #075e54;
      color: #fff;
      font-size: 20px;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      transition: background .15s;
    }
    .input-bar button:hover    { background: #128c7e; }
    .input-bar button:disabled { background: #bdbdbd; cursor: default; }
  </style>
</head>
<body>

<div class="header">
  <div class="avatar">🏥</div>
  <div class="header-info">
    <h2>Clínica de Exames</h2>
    <p>Assistente Virtual</p>
  </div>
</div>

<div class="messages" id="msgs"></div>

<div class="input-bar">
  <input id="txt" type="text" placeholder="Digite uma mensagem…" autocomplete="off" />
  <button id="btn" title="Enviar">&#9658;</button>
</div>

<script>
  const msgs   = document.getElementById('msgs');
  const txt    = document.getElementById('txt');
  const btn    = document.getElementById('btn');

  // Persist session across page refreshes
  let sessionId = localStorage.getItem('clinica_session');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('clinica_session', sessionId);
  }

  function now() {
    return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  }

  function addBubble(text, who) {
    const div = document.createElement('div');
    div.className = `bubble ${who}-bubble`;
    const safe = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    div.innerHTML = safe + `<div class="time">${now()}</div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function showTyping() {
    const d = document.createElement('div');
    d.className = 'typing'; d.id = 'typing';
    d.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function hideTyping() {
    document.getElementById('typing')?.remove();
  }

  async function send() {
    const text = txt.value.trim();
    if (!text) return;
    txt.value = '';
    btn.disabled = true;
    addBubble(text, 'user');
    showTyping();
    try {
      const res  = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      const data = await res.json();
      hideTyping();
      addBubble(data.response ?? 'Sem resposta.', 'bot');
    } catch {
      hideTyping();
      addBubble('Erro ao conectar com o servidor.', 'bot');
    }
    btn.disabled = false;
    txt.focus();
  }

  btn.addEventListener('click', send);
  txt.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) send(); });

  // Welcome message
  setTimeout(() => {
    addBubble('Olá! 👋 Sou o assistente virtual da Clínica de Exames.\\nComo posso te ajudar hoje?', 'bot');
    txt.focus();
  }, 400);
</script>

</body>
</html>"""


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
async def demo_page():
    return HTMLResponse(_DEMO_HTML)


@router.post("/chat")
async def chat(req: ChatRequest):
    graph = get_graph()
    config = {"configurable": {"thread_id": req.session_id}}
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": req.message}], "phone": req.session_id, "intent": None},
        config=config,
    )
    last = result["messages"][-1]
    logger.info("Demo chat [%s]: %s → %s", req.session_id[:8], req.message, last.content[:80])
    return {"response": last.content}
