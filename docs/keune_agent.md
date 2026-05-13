# Agente Keune Brasil — Lara

Configuração white-label do Sales Agent para a [Keune Brasil](https://www.keune.com.br/), marca holandesa premium de haircare profissional fundada em 1922.

## Quem é a Lara

Consultora virtual oficial da Keune Brasil no WhatsApp. Personalidade:
- **Tom**: elegante, próxima, confiante, técnica sem ser fria
- **Conhecimento**: terminologia capilar (pH, queratina, fios cacheados/lisos, química)
- **Posicionamento**: consultora — não vendedora agressiva

## Como ativar

No `.env`:
```bash
AGENT_BRAND=keune
USE_AI_AGENT=true
OPENAI_API_KEY=sk-...
```

O `AISalesHandler` detecta a flag e instancia automaticamente o `KeuneSalesAgent` em vez do agente genérico.

## Dois fluxos de atendimento

A Lara identifica logo no início se é **profissional** (cabeleireiro/salão) ou **consumidor final** e adapta:

### B2C — Consumidor final
1. **Greeting** → identifica perfil
2. **Diagnóstico** → tipo de fio, condição (química?), queixa principal, rotina atual
3. **Pitch** → recomenda UM kit baseado no diagnóstico (não 5 opções)
4. **Objeções** → trata sem ofertar desconto na primeira rodada
5. **Direcionamento** → site keune.com.br ou salão parceiro mais próximo

### B2B — Profissional
1. **Identificação** → cidade, estabelecimento, já é cliente Keune?
2. **Interesse** → quais linhas (Color, So Pure, Care)
3. **Handoff técnico** → conecta com representante regional via `conectar_representante`
4. A Lara **não fecha venda B2B** — o representante faz isso

## Catálogo

[workers/agents/configs/keune/catalog.py](../workers/agents/configs/keune/catalog.py) contém ~18 produtos das linhas:

| Linha | Público | Hero products |
|-------|---------|---------------|
| **Care** | B2C + B2B | Vital Nutrition, Keratin Smooth, Satin Oil |
| **So Pure** | B2C + B2B | Calming, Energizing, Color Care (94% natural, vegano) |
| **Style** | B2C + B2B | Liquid Definer, Defining Lotion |
| **Color** | B2B apenas | Tinta Color, So Pure Color |
| **Man** | B2C + B2B | Refreshing Shampoo, Texture Cream |
| **Blend** | B2C + B2B | Blend Curls, Curl Defining Cream |

E 6 kits pré-mapeados por perfil capilar (`seco_quimica`, `cacheado_definicao`, `couro_sensivel`, `queda_fortalecimento`, `colorido_manutencao`, `masculino_diario`).

> ⚠️ **Preços do catálogo são placeholders representativos** — em produção, substituir por integração com o e-commerce oficial.

## Knowledge Base

[workers/agents/configs/keune/knowledge.py](../workers/agents/configs/keune/knowledge.py):
- **FAQ** com 11 perguntas frequentes (onde comprar, veganismo, cruelty-free, uso pós-progressiva, etc)
- **Diagnóstico capilar** mapeando 9 queixas → linhas Keune
- **Representantes regionais** (Sudeste, Sul, Nordeste, Norte, Centro-Oeste)

Perguntas marcadas com `"HANDOFF"` na FAQ disparam transferência automática para humano (produto vencido, troca, NF).

## Tools Keune-specific

[workers/agents/configs/keune/tools.py](../workers/agents/configs/keune/tools.py):

| Tool | Quando usar |
|------|-------------|
| `consultar_catalogo_keune` | Filtrar produtos por linha, público, tipo ou indicação |
| `recomendar_kit_keune` | Sugerir combo (shampoo + cond + tratamento) por perfil |
| `consultar_faq_keune` | Responder perguntas frequentes com texto oficial |
| `diagnosticar_queixa` | Mapear queixa → linha indicada |
| `conectar_representante` | Handoff B2B com representante regional |
| `localizar_salao_parceiro` | Indicar onde comprar presencialmente (B2C) |

Mais as tools globais `transferir_humano` e `agendar_followup`.

## Guardrails específicos Keune

A persona ([persona.py](../workers/agents/configs/keune/persona.py)) define regras duras:

1. **Nunca prescrever para condição médica** (alopecia, dermatite, queda intensa) → encaminhar dermatologista
2. **Nunca prometer resultado garantido** em coloração/alisamento — "cada cabelo responde diferente"
3. **Nunca depreciar concorrente** (L'Oréal, Wella, Truss, Schwarzkopf) — reconhecer e diferenciar
4. **Nunca inventar ingrediente ou modo de uso** — sempre usar `consultar_catalogo_keune`
5. **Identificar B2C vs B2B cedo** — o atendimento muda radicalmente

## Exemplos de conversa

### Exemplo 1 — B2C com cabelo seco e química
```
Cliente: Oi, queria saber qual shampoo Keune é bom pra cabelo ressecado
Lara:   Oi! Aqui é a Lara da Keune 💛 Conta pra mim — você usa alguma química
        no cabelo (coloração, progressiva, mechas)?
Cliente: Sim, faço progressiva a cada 6 meses
Lara:   Entendi! Pra cabelo com química e ressecamento, a linha indicada é
        a *Keratin Smooth + Vital Nutrition*:

        *Keratin Smooth Shampoo* — mantém o efeito da progressiva
        *Vital Nutrition Conditioner* — devolve maciez aos fios ressecados
        *Vital Nutrition Mask* — tratamento 1-2x por semana

        Quer que eu te mande onde encontrar?
```

### Exemplo 2 — B2B (cabeleireira)
```
Cliente: Oi, sou cabeleireira em SP e queria conhecer a linha de coloração
Lara:   Oi! Que ótimo 💼 Aqui é a Lara da Keune. Vou te conectar com
        nosso representante de SP que organiza tabela profissional,
        treinamento e amostras. Me passa só:
        - Nome do salão
        - Cidade/bairro
        - Já trabalha com alguma coloração Keune ou seria primeira vez?
```

### Exemplo 3 — Handoff por reclamação
```
Cliente: Comprei um produto e veio com defeito, péssimo!
Lara:   [usa transferir_humano com reason=complaint, priority=urgent]
        Entendi a situação. Vou passar pro nosso atendimento
        especializado agora mesmo. Você é respondida em até 2h 💛
```

## Customizando ainda mais

Para ajustar para campanha específica (Black Friday, lançamento, etc.):

1. Edite `KEUNE_SYSTEM_PROMPT` em [persona.py](../workers/agents/configs/keune/persona.py)
2. Adicione produtos sazonais em [catalog.py](../workers/agents/configs/keune/catalog.py)
3. Atualize FAQ em [knowledge.py](../workers/agents/configs/keune/knowledge.py) com FAQ da campanha
4. Adicione tool específica em [tools.py](../workers/agents/configs/keune/tools.py) (ex: `verificar_cupom_blackfriday`)

Sem precisar tocar no agente base.
