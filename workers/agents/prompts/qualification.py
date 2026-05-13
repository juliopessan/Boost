"""
Prompts da fase de qualificação BANT (Budget, Authority, Need, Timeline).
Aplicado depois do greeting, antes da apresentação do produto.
"""

QUALIFICATION_PROMPT = """Você está qualificando este lead. Use a metodologia BANT adaptada ao WhatsApp.

# REGRAS DE QUALIFICAÇÃO
- Faça UMA pergunta por mensagem (WhatsApp não é formulário).
- Trabalhe na ordem: Necessidade → Urgência → Volume/Orçamento → Decisor.
- Se o cliente já forneceu uma informação, NÃO repita a pergunta.
- Após coletar 3 das 4 dimensões → avance para apresentação de produto.

# O QUE JÁ SABEMOS DO CLIENTE
{qualified_data}

# DIMENSÕES PENDENTES
{pending_dimensions}

# ÚLTIMA MENSAGEM DO CLIENTE
"{user_message}"

# SUA TAREFA
1. Extraia o que o cliente disse e atualize o JSON de qualificação.
2. Se ainda faltam dimensões → faça a próxima pergunta natural.
3. Se já tem informação suficiente → sinalize avanço para a próxima fase.

Responda em JSON estrito:
{{
  "extracted_data": {{
    "need": "...",
    "urgency": "...",
    "volume": "...",
    "decision_maker": "..."
  }},
  "next_action": "ask_question" | "advance_to_pitch",
  "whatsapp_response": "texto da próxima mensagem WhatsApp (máx. 3 linhas)"
}}
"""


QUALIFICATION_QUESTIONS = {
    "need": [
        "O que você está buscando exatamente? Pra qual uso?",
        "Me conta um pouco mais — é pra empresa ou uso pessoal?",
        "Qual o problema que você quer resolver com isso?",
    ],
    "urgency": [
        "Quando você precisa começar a usar?",
        "Tem alguma data específica em mente?",
        "É algo pra agora ou pode ser nas próximas semanas?",
    ],
    "volume": [
        "Tem uma ideia de quanto pretende investir?",
        "Qual o volume que você precisa?",
        "Seria pra quantas pessoas/unidades?",
    ],
    "decision_maker": [
        "A decisão é só sua ou precisa alinhar com mais alguém?",
        "Você é a pessoa que aprova a compra?",
    ],
}
