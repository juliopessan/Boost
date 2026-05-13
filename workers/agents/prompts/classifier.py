"""
Prompt classificador de intenção — primeira camada antes de rotear para o agente certo.
"""

INTENT_CLASSIFIER_PROMPT = """Classifique a intenção da mensagem do cliente no WhatsApp.

# MENSAGEM
"{user_message}"

# CONTEXTO DA SESSÃO
- Estágio atual: {current_stage}
- Última mensagem do agente: "{last_agent_message}"

# INTENÇÕES POSSÍVEIS

| Intenção | Descrição | Exemplos |
|----------|-----------|----------|
| `greeting` | Saudação inicial | "Oi", "Olá", "Boa tarde" |
| `product_inquiry` | Pergunta sobre produto | "Tem o iPhone 15?", "Quanto custa X?" |
| `qualification_response` | Respondendo qualificação | "É pra empresa", "5 unidades" |
| `objection` | Resistência/objeção | "Tá caro", "Vou pensar" |
| `buying_signal` | Sinal de compra | "Pode fechar", "Quero levar" |
| `support` | Suporte/problema | "Meu pedido não chegou", "Problema com X" |
| `human_request` | Pede humano | "Quero falar com atendente", "Pessoa de verdade" |
| `complaint` | Reclamação séria | "Vou processar", "Procon" |
| `off_topic` | Fora do escopo | Conversa sem relação a vendas |
| `unclear` | Não dá pra entender | Mensagem confusa, áudio, sticker |

# REGRAS DE CLASSIFICAÇÃO
- Se cliente pede humano EM QUALQUER MOMENTO → `human_request` (prioridade máxima)
- Se mensagem tem ofensa, ameaça legal, palavrão dirigido → `complaint` (transferir)
- Se é continuação natural do estágio atual → priorize a intenção esperada
- Em caso de dúvida → `unclear`

# SAÍDA EM JSON ESTRITO
{{
  "intent": "...",
  "confidence": 0.0 a 1.0,
  "extracted_entities": {{
    "product_mentioned": "...",
    "quantity": ...,
    "sentiment": "positive" | "neutral" | "negative"
  }},
  "should_transfer_to_human": true | false,
  "reasoning": "breve explicação em 1 frase"
}}
"""


HUMAN_HANDOFF_PROMPT = """Você precisa transferir o cliente para um atendente humano.

# MOTIVO DA TRANSFERÊNCIA
{handoff_reason}

# REGRAS
1. NÃO peça desculpas excessivas — seja direta e prestativa.
2. Informe o prazo realista de resposta humana.
3. Resuma o contexto que o humano vai precisar.
4. Tom: tranquilizador, não defensivo.

# DADOS A REGISTRAR NO TICKET
- Resumo da conversa: {conversation_summary}
- Última intenção identificada: {last_intent}
- Prioridade: {priority}

Mensagem WhatsApp para o cliente (máx. 3 linhas):
"""
