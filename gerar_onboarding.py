# -*- coding: utf-8 -*-
"""Script temporario para gerar o DOCX de onboarding do cliente."""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def body(doc, text):
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(11)
    return p


def step(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.add_run(text).font.size = Pt(11)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("[ Imagem: " + text + " ]")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run.font.italic = True
    return p


def note(doc, text):
    p = doc.add_paragraph()
    run = p.add_run("ATENCAO: " + text)
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xCC, 0x66, 0x00)
    return p


doc = Document()

# Titulo
doc.add_heading("Guia de Configuracao - Bot de Atendimento WhatsApp", 0)
body(doc, (
    "Este documento orienta voce a configurar as contas e gerar as credenciais "
    "necessarias para o funcionamento do bot. Siga cada etapa na ordem indicada e "
    "envie os dados ao seu desenvolvedor ao final."
))
doc.add_paragraph()

# PARTE 1 - OpenAI
doc.add_heading("Parte 1 - OpenAI (Inteligencia Artificial do Bot)", level=1)
body(doc, (
    "O bot utiliza a inteligencia artificial da OpenAI (ChatGPT) para entender e "
    "responder as mensagens dos seus pacientes. Voce precisara criar uma conta e "
    "adicionar um metodo de pagamento. A cobranca e por uso - em clinicas de pequeno "
    "e medio porte o custo mensal costuma ficar entre R$ 10 e R$ 50."
))

doc.add_heading("1.1  Criar conta na OpenAI", level=2)
step(doc, 'Acesse platform.openai.com e clique em "Sign up".')
caption(doc, "Tela inicial do site platform.openai.com com o botao Sign up destacado")

step(doc, "Cadastre-se com seu e-mail ou conta Google.")
caption(doc, "Formulario de cadastro com campos de e-mail e senha")

step(doc, "Confirme o e-mail recebido na sua caixa de entrada.")
caption(doc, "E-mail de confirmacao da OpenAI na caixa de entrada")

doc.add_heading("1.2  Adicionar metodo de pagamento", level=2)
step(doc, 'Apos o login, clique no seu nome (canto superior direito) e selecione "Billing".')
caption(doc, "Menu do usuario aberto com a opcao Billing destacada")

step(doc, 'Clique em "Add payment method" e informe os dados do cartao de credito.')
caption(doc, "Tela de Billing com o botao Add payment method")

step(doc, 'Defina um limite de gasto mensal em "Usage limits" para evitar surpresas (sugestao: R$ 100).')
caption(doc, "Tela de Usage limits com campo de valor preenchido")

doc.add_heading("1.3  Gerar a chave de API (API Key)", level=2)
step(doc, 'No menu lateral, clique em "API keys".')
caption(doc, "Menu lateral da plataforma OpenAI com API keys selecionado")

step(doc, 'Clique em "Create new secret key", de um nome (ex.: "bot-clinica") e clique em "Create".')
caption(doc, "Modal de criacao de chave com campo de nome preenchido e botao Create")

step(doc, 'Copie a chave exibida (comeca com "sk-..."). Ela so e exibida uma vez.')
caption(doc, "Chave gerada exibida na tela com botao de copiar destacado")

note(doc, "Guarde essa chave em local seguro. Nao compartilhe publicamente.")

doc.add_paragraph()
body(doc, "DADO NECESSARIO: a chave sk-... gerada no passo 1.3.")

# PARTE 2 - Z-API
doc.add_page_break()
doc.add_heading("Parte 2 - Z-API (Canal WhatsApp)", level=1)
body(doc, (
    "O Z-API conecta o bot ao seu numero de WhatsApp sem precisar de aprovacao da Meta. "
    "Voce usara o numero de telefone da sua clinica - o mesmo chip que deseja usar para "
    "atendimento. O plano e pago mensalmente direto no site do Z-API."
))

note(doc, (
    "Use um numero que NAO esteja cadastrado como WhatsApp pessoal. "
    "O ideal e um chip dedicado ao atendimento da clinica."
))

doc.add_heading("2.1  Criar conta no Z-API", level=2)
step(doc, 'Acesse z-api.io e clique em "Criar conta gratis".')
caption(doc, "Pagina inicial do z-api.io com botao Criar conta gratis destacado")

step(doc, "Preencha nome, e-mail e senha, e confirme o cadastro.")
caption(doc, "Formulario de cadastro do Z-API preenchido")

doc.add_heading("2.2  Criar uma instancia", level=2)
body(doc, (
    "Cada instancia equivale a uma conexao WhatsApp. Para a clinica, voce precisara "
    "de uma instancia."
))
step(doc, 'No painel, clique em "Nova instancia".')
caption(doc, "Painel do Z-API com botao Nova instancia destacado")

step(doc, 'De um nome a instancia (ex.: "clinica-exames") e confirme.')
caption(doc, "Modal de criacao de instancia com campo de nome preenchido")

step(doc, "Selecione um plano e finalize o pagamento.")
caption(doc, "Tela de selecao de plano do Z-API")

doc.add_heading("2.3  Conectar o numero de WhatsApp (QR Code)", level=2)
step(doc, 'Abra a instancia criada e clique em "Conectar".')
caption(doc, "Tela da instancia com botao Conectar e QR Code exibido")

step(doc, 'No celular da clinica, abra o WhatsApp -> Menu (tres pontos) -> "Dispositivos vinculados" -> "Vincular dispositivo".')
caption(doc, "Tela do WhatsApp no celular com a opcao Dispositivos vinculados aberta")

step(doc, 'Aponte a camera para o QR Code exibido no Z-API. A instancia ficara com status "Conectado".')
caption(doc, "Status da instancia no Z-API exibindo Conectado com icone verde")

doc.add_heading("2.4  Copiar as credenciais", level=2)
body(doc, "Voce precisara de tres informacoes dentro da instancia:")

step(doc, "Instance ID - exibido no topo da pagina da instancia.")
caption(doc, "Tela da instancia com o campo Instance ID destacado")

step(doc, "Token - exibido logo abaixo do Instance ID.")
caption(doc, "Tela da instancia com o campo Token destacado")

step(doc, 'Client Token (Security Token) - acesse a aba "Security" dentro da instancia e copie o valor exibido.')
caption(doc, "Aba Security da instancia com o campo Client Token destacado")

doc.add_paragraph()
body(doc, "DADOS NECESSARIOS: Instance ID, Token e Client Token copiados no passo 2.4.")

# PARTE 3 - Enviar credenciais
doc.add_page_break()
doc.add_heading("Parte 3 - Enviar as credenciais ao desenvolvedor", level=1)
body(doc, (
    "Com os dados abaixo em maos, envie-os ao seu desenvolvedor pelo canal combinado "
    "(WhatsApp, e-mail ou formulario seguro). Nao publique essas informacoes em grupos "
    "ou redes sociais."
))

doc.add_paragraph()
table = doc.add_table(rows=5, cols=2)
table.style = "Table Grid"

header_row = table.rows[0]
header_row.cells[0].text = "Dado"
header_row.cells[1].text = "Valor"
for cell in header_row.cells:
    cell.paragraphs[0].runs[0].font.bold = True

rows_data = [
    ("OpenAI API Key", "sk-..."),
    ("Z-API Instance ID", ""),
    ("Z-API Token", ""),
    ("Z-API Client Token", ""),
]
for i, (label, value) in enumerate(rows_data, start=1):
    table.rows[i].cells[0].text = label
    table.rows[i].cells[1].text = value

doc.add_paragraph()
note(doc, (
    "Apos o desenvolvedor confirmar a configuracao, voce pode descartar "
    "este documento ou guarda-lo em local seguro offline."
))

# RESUMO
doc.add_page_break()
doc.add_heading("Resumo - O que cada servico faz", level=1)
table2 = doc.add_table(rows=4, cols=3)
table2.style = "Table Grid"

h2 = ["Servico", "Funcao", "Quem paga"]
for i, h in enumerate(h2):
    table2.rows[0].cells[i].text = h
    table2.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

rows2 = [
    ("OpenAI", "Inteligencia do bot (entende e responde mensagens)", "Voce (cliente)"),
    ("Z-API", "Conexao com seu numero de WhatsApp", "Voce (cliente)"),
    ("Hospedagem (Render)", "Servidor onde o bot fica rodando 24h", "Desenvolvedor"),
]
for i, cols in enumerate(rows2, start=1):
    for j, val in enumerate(cols):
        table2.rows[i].cells[j].text = val

doc.add_paragraph()
body(doc, "Duvidas? Entre em contato com seu desenvolvedor.")

doc.save("onboarding_cliente.docx")
print("Arquivo gerado: onboarding_cliente.docx")
