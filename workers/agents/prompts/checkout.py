"""
Prompts da fase de checkout — coleta de dados, confirmação de pedido e pós-venda.
"""

CHECKOUT_PROMPT = """O cliente decidiu comprar. Vamos coletar os dados necessários.

# DADOS NECESSÁRIOS PARA O PEDIDO
{required_fields}

# DADOS JÁ COLETADOS
{collected_data}

# CAMPO ATUAL
{current_field}

# REGRAS
1. Peça UM dado por vez.
2. Valide o formato antes de avançar:
   - CPF: 11 dígitos, validar dígito verificador
   - CEP: 8 dígitos, consultar via ViaCEP
   - E-mail: formato válido
   - Telefone: já temos (é o do WhatsApp)
3. Se cliente errou o formato → peça novamente com exemplo.
4. Após coletar TUDO → mostre resumo do pedido e peça confirmação.

# MENSAGEM DO CLIENTE
"{user_message}"

Resposta JSON:
{{
  "field_validated": true | false,
  "extracted_value": "...",
  "error_message": "...",
  "next_field": "...",
  "whatsapp_response": "..."
}}
"""


ORDER_CONFIRMATION_PROMPT = """Apresente o resumo final do pedido para confirmação.

# PEDIDO
- Produto: {product}
- Quantidade: {quantity}
- Preço unitário: {unit_price}
- Subtotal: {subtotal}
- Desconto: {discount}
- Frete: {shipping}
- **Total: {total}**

# CLIENTE
- Nome: {customer_name}
- CPF: {customer_cpf}
- Endereço: {address}

# PAGAMENTO
- Forma: {payment_method}

# FORMATO WHATSAPP
Estruture com quebras de linha e *negrito*. Termine com botões Confirmar/Cancelar.

Exemplo de estrutura:
*Resumo do seu pedido:*
[produto] x [qtd]
Total: *R$ X,XX*

Entrega: [endereço resumido]
Pagamento: [forma]

Confirma?
"""


POST_SALE_PROMPT = """Pedido confirmado. Envie a mensagem de pós-venda.

# DADOS DA CONFIRMAÇÃO
- Número do pedido: {order_id}
- Prazo de entrega: {delivery_estimate}
- Link de rastreamento: {tracking_link}
- Nota fiscal: será enviada em {invoice_eta}

# OBJETIVOS DA MENSAGEM
1. Agradecer a compra
2. Confirmar dados-chave (nº pedido, prazo)
3. Definir expectativa de próximos passos
4. Abrir canal para dúvidas
5. Pedir avaliação suave (NPS)

# FORMATO
2-3 mensagens curtas em sequência. Tom caloroso.
"""
