"""
Base de conhecimento Keune — FAQ + diagnóstico capilar.
Usado para grounding do agente em perguntas frequentes.
"""

KEUNE_FAQ = {
    "onde_comprar": {
        "pergunta": "Onde comprar produtos Keune?",
        "resposta": (
            "Você encontra a Keune em três canais:\n"
            "• Site oficial: keune.com.br\n"
            "• Salões parceiros (rede de cabeleireiros credenciados)\n"
            "• Distribuidores autorizados\n"
            "Posso te ajudar a achar o canal mais próximo. Em que cidade você está?"
        ),
    },
    "produtos_veganos": {
        "pergunta": "Quais produtos Keune são veganos?",
        "resposta": (
            "Toda a linha *So Pure* é vegana e tem 94% de ingredientes naturais. "
            "Inclui Calming (couro cabeludo sensível), Energizing (fortalecimento) e Color Care (cabelo colorido)."
        ),
    },
    "testes_animais": {
        "pergunta": "Keune testa em animais?",
        "resposta": (
            "A Keune é uma marca cruelty-free. Não realizamos testes em animais em nenhuma etapa do desenvolvimento dos produtos."
        ),
    },
    "diferenca_keune_outras": {
        "pergunta": "O que diferencia a Keune de outras marcas profissionais?",
        "resposta": (
            "A Keune é uma marca familiar holandesa fundada em 1922 — quatro gerações dedicadas ao haircare. "
            "O que muda na prática: pesquisa própria, fórmulas com qualidade europeia e foco em tratamento "
            "(não só estética). É uma marca que cabeleireiros usam pelo resultado técnico."
        ),
    },
    "uso_pos_progressiva": {
        "pergunta": "Posso usar Keune depois de fazer progressiva/alisamento?",
        "resposta": (
            "Sim — a linha *Keratin Smooth* foi desenvolvida exatamente para manter o efeito de tratamentos "
            "de selagem por mais tempo, com fórmula que não 'tira' o liso."
        ),
    },
    "duracao_produto": {
        "pergunta": "Quanto tempo dura um shampoo Keune?",
        "resposta": (
            "Um shampoo de 300ml dura em média 3-4 meses no uso diário (cabelo médio). "
            "A versão de 1L é o melhor custo-benefício se você lava com frequência."
        ),
    },
    "cabelo_oleoso": {
        "pergunta": "Tenho cabelo oleoso, qual Keune indicado?",
        "resposta": (
            "Para couro cabeludo oleoso, recomendo o *So Pure Energizing* — limpa profundamente sem "
            "ressecar e tem hortelã que dá frescor."
        ),
    },
    "primeiras_unidades": {
        "pergunta": "Por onde começar com Keune? Qual o primeiro produto?",
        "resposta": (
            "O caminho mais seguro é começar pelo *kit de cuidado básico*: shampoo + condicionador da "
            "linha que combina com seu cabelo. Em 30-45 dias você já sente diferença. "
            "Me conta como é seu cabelo que te indico o ideal."
        ),
    },
    "salao_distribuidor": {
        "pergunta": "Sou cabeleireira, como me torno parceira / compro com preço profissional?",
        "resposta": (
            "Perfeito! Vou te conectar com o representante Keune da sua região — ele organiza cadastro, "
            "preços profissionais, treinamento e amostras."
        ),
    },
    "produto_vencido": {
        "pergunta": "Recebi um produto com problema / vencimento / dúvida sobre lote",
        "resposta": "HANDOFF",  # sempre transferir para humano
    },
    "troca_devolucao": {
        "pergunta": "Como funciona troca / devolução / NF?",
        "resposta": "HANDOFF",
    },
}


DIAGNOSTICO_CAPILAR = {
    "tipos_fio": {
        "liso": "Fio reto, sem ondulação natural. Tende a oleosidade na raiz, brilho fácil.",
        "ondulado": "Ondas em formato de S. Pode ter frizz e ressecamento nas pontas.",
        "cacheado": "Cachos definidos em formato espiral. Tende a ressecamento e precisa de hidratação constante.",
        "crespo": "Curvatura muito fechada, formato 4A-4C. Maior fragilidade e necessidade de nutrição/lubrificação.",
    },
    "condicoes": {
        "natural": "Sem química — fios virgens",
        "coloracao": "Tingimento permanente — cabelo precisa de cuidado anti-desbote",
        "descoloracao": "Loiro, mechas — fios mais sensibilizados, precisam de reconstrução",
        "progressiva": "Selagem com química — manter com produtos sem sal (não é o caso da Keune, todas são sem sal)",
        "alisamento": "Alisamento permanente — cuidado anti-queda e reposição de massa",
        "permanente": "Permanente de cachos ou tonalizante — cuidado de hidratação",
    },
    "queixas_x_linha": {
        "ressecamento": ["Care Vital Nutrition", "Care Keratin Smooth"],
        "frizz": ["Care Keratin Smooth", "Care Satin Oil"],
        "queda": ["So Pure Energizing"],
        "oleosidade": ["So Pure Energizing", "So Pure Calming"],
        "couro_sensivel": ["So Pure Calming"],
        "volume_excessivo": ["Care Keratin Smooth"],
        "falta_definicao_cachos": ["Blend Curls", "Style Liquid Definer"],
        "cor_desbotando": ["So Pure Color Care"],
        "danificado_quimica": ["Care Vital Nutrition", "Care Keratin Smooth"],
    },
}


REPRESENTANTES_REGIONAIS = {
    # Mock — em produção vem do CRM
    "sudeste": {"nome": "Time Sudeste", "email": "sudeste@keune.com.br", "tempo_resposta": "1 dia útil"},
    "sul": {"nome": "Time Sul", "email": "sul@keune.com.br", "tempo_resposta": "1 dia útil"},
    "nordeste": {"nome": "Time Nordeste", "email": "nordeste@keune.com.br", "tempo_resposta": "2 dias úteis"},
    "norte": {"nome": "Time Norte", "email": "norte@keune.com.br", "tempo_resposta": "2 dias úteis"},
    "centro_oeste": {"nome": "Time Centro-Oeste", "email": "centrooeste@keune.com.br", "tempo_resposta": "1 dia útil"},
}


def consultar_faq(termo: str) -> dict | None:
    """Busca FAQ por palavra-chave."""
    termo_lower = termo.lower()
    for key, faq in KEUNE_FAQ.items():
        if termo_lower in key or termo_lower in faq["pergunta"].lower():
            return {"key": key, **faq}
    return None


def sugerir_linhas_por_queixa(queixa: str) -> list[str]:
    """Mapeia queixa do cliente para linha(s) Keune recomendada(s)."""
    queixa_lower = queixa.lower()
    for key, linhas in DIAGNOSTICO_CAPILAR["queixas_x_linha"].items():
        if key in queixa_lower or queixa_lower in key:
            return linhas
    return []
