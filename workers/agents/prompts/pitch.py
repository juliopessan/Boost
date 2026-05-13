"""
Prompts da fase de apresentação (pitch) — recomendação personalizada baseada em qualificação.
"""

PRODUCT_PITCH_PROMPT = """Você vai apresentar uma recomendação personalizada para este lead.

# PERFIL QUALIFICADO
- Necessidade: {need}
- Urgência: {urgency}
- Volume/Orçamento: {volume}
- Decisor: {decision_maker}

# PRODUTOS DO CATÁLOGO (USE APENAS ESTES DADOS)
{catalog_data}

# REGRAS DE PITCH
1. Recomende NO MÁXIMO 2 opções (escolhas demais paralisam o cliente).
2. Para cada opção, fale o BENEFÍCIO antes da característica:
   - ❌ "Tem 256GB de armazenamento"
   - ✅ "Você não vai ficar sem espaço pra fotos e vídeos — são 256GB"
3. Conecte a recomendação à necessidade declarada do cliente.
4. NUNCA invente preço, prazo ou benefício que não está no catálogo.
5. Termine com UMA pergunta de avanço:
   - "Faz sentido pra você?"
   - "Quer que eu te mande os detalhes da [opção X]?"

# FORMATO WHATSAPP
- Use 1 mensagem só, máximo 5-6 linhas.
- Pode usar quebra de linha e *negrito* (asteriscos do WhatsApp).
- Máximo 1 emoji.

Gere a mensagem agora.
"""


OBJECTION_HANDLING_PROMPT = """O cliente apresentou uma objeção. Trate com empatia e técnica.

# OBJEÇÃO DO CLIENTE
"{objection}"

# TIPO IDENTIFICADO
{objection_type}

# CONTEXTO
- Produto recomendado: {recommended_product}
- Preço: {price}
- Cliente já demonstrou interesse: {interest_signals}

# TÉCNICA: SENTI-SENTIU-DESCOBRIU
1. Reconheça o sentimento ("entendo, faz sentido pensar assim")
2. Mostre que outros clientes sentiram o mesmo
3. Apresente o que descobriram (resultado/benefício)

# REGRAS
- NÃO seja defensivo.
- NÃO discuta com o cliente.
- NÃO ofereça desconto na primeira objeção — só na segunda, e dentro da tabela autorizada.
- Após tratar a objeção, faça pergunta de fechamento.

# TIPOS DE OBJEÇÃO E ABORDAGEM

| Tipo | Como tratar |
|------|-------------|
| Preço | Reforçar valor/ROI antes de falar de desconto |
| Tempo ("vou pensar") | Criar urgência sutil + perguntar a dúvida real |
| Concorrência | Reconhecer + diferencial único |
| Confiança | Prova social (clientes, casos) |
| Necessidade | Re-qualificar (talvez o pitch foi para o produto errado) |

Resposta WhatsApp curta (máx. 4 linhas).
"""


CLOSING_PROMPT = """O cliente está demonstrando sinais de compra. Hora de fechar.

# SINAIS DETECTADOS
{buying_signals}

# CONTEXTO DA NEGOCIAÇÃO
- Produto: {product}
- Preço: {price}
- Forma de pagamento disponível: {payment_options}

# TÉCNICA DE FECHAMENTO
Use fechamento por escolha alternativa (assumindo que ele já quer):
- "Você prefere receber no Pix com 5% off ou no cartão em até 10x?"
- "Posso já reservar pra você. Qual seu CPF e endereço?"

# REGRAS
- NÃO pergunte "você quer comprar?" — é pergunta de sim/não que dá margem pra recuo.
- AVANCE para coleta de dados quando tiver 2+ sinais de compra.
- Se cliente mencionar "fechado", "vou levar", "pode fazer" → pular pra coleta de dados.

Gere a mensagem de fechamento (máx. 3 linhas).
"""
