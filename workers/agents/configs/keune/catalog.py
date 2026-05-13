"""
Catálogo Keune Brasil — produtos retail (B2C) e profissionais (B2B).

Fonte: keune.com.br (validar preços com a equipe — valores aqui são placeholders
representativos para o agente raciocinar sobre diagnóstico → produto).

Em produção, substituir por consulta ao e-commerce oficial via API.
"""

KEUNE_CATALOG = {
    # ─────────── LINHA CARE ───────────
    "care_vital_nutrition_shampoo": {
        "id": "care_vital_nutrition_shampoo",
        "linha": "Care",
        "nome": "Vital Nutrition Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["300ml", "1000ml"],
        "preco_300ml": 119.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo seco", "danificado", "quebradiço", "sem brilho"],
        "tipo_fio": ["liso", "ondulado", "cacheado"],
        "beneficios": [
            "nutrição profunda em fios secos",
            "devolve maciez e brilho",
            "reduz quebra com uso contínuo",
        ],
        "ingredientes_destaque": ["óleo de abacate", "queratina vegetal", "proteínas"],
        "modo_uso": "Aplicar nos fios molhados, massagear suavemente e enxaguar. Repetir se necessário.",
    },
    "care_vital_nutrition_conditioner": {
        "id": "care_vital_nutrition_conditioner",
        "linha": "Care",
        "nome": "Vital Nutrition Conditioner",
        "tipo": "condicionador",
        "tamanhos": ["250ml", "1000ml"],
        "preco_250ml": 129.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo seco", "danificado"],
        "beneficios": ["selagem das cutículas", "desembaraço sem peso", "brilho instantâneo"],
        "modo_uso": "Após o shampoo, aplicar nos comprimentos e pontas. Deixar agir 1-3min e enxaguar.",
    },
    "care_vital_nutrition_mask": {
        "id": "care_vital_nutrition_mask",
        "linha": "Care",
        "nome": "Vital Nutrition Mask",
        "tipo": "mascara",
        "tamanhos": ["200ml", "500ml"],
        "preco_200ml": 189.00,
        "publico": "B2C+B2B",
        "indicado_para": ["nutrição intensa", "fios muito ressecados"],
        "beneficios": ["tratamento semanal de nutrição profunda", "restaura elasticidade"],
        "modo_uso": "1-2x por semana após o shampoo. Deixar agir 5-10min e enxaguar.",
    },
    "care_satin_oil": {
        "id": "care_satin_oil",
        "linha": "Care",
        "nome": "Satin Oil",
        "tipo": "leave-in/finalizador",
        "tamanhos": ["95ml"],
        "preco": 159.00,
        "publico": "B2C+B2B",
        "indicado_para": ["frizz", "pontas ressecadas", "brilho", "termoproteção leve"],
        "beneficios": ["finalização sedosa", "controle de frizz", "termoproteção até 200°C"],
        "modo_uso": "1-2 gotas nos fios úmidos ou secos, focando nos comprimentos.",
    },
    "care_keratin_smooth_shampoo": {
        "id": "care_keratin_smooth_shampoo",
        "linha": "Care",
        "nome": "Keratin Smooth Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["300ml", "1000ml"],
        "preco_300ml": 129.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo com química", "progressiva", "alisamento", "frizz"],
        "beneficios": ["mantém efeito de tratamentos de selagem", "anti-frizz", "fios alinhados"],
        "ingredientes_destaque": ["queratina hidrolisada", "óleo de argan"],
    },

    # ─────────── LINHA SO PURE (94% natural / vegana) ───────────
    "sopure_calming_shampoo": {
        "id": "sopure_calming_shampoo",
        "linha": "So Pure",
        "nome": "So Pure Calming Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["250ml", "1000ml"],
        "preco_250ml": 139.00,
        "publico": "B2C+B2B",
        "indicado_para": ["couro cabeludo sensível", "coceira", "vermelhidão", "uso diário"],
        "tipo_fio": ["todos"],
        "selo": "94% natural / vegano / livre de sulfato",
        "beneficios": ["acalma couro cabeludo", "limpeza suave para uso diário", "fragrância de lavanda"],
        "ingredientes_destaque": ["óleo essencial de lavanda", "óleo de jojoba"],
    },
    "sopure_energizing_shampoo": {
        "id": "sopure_energizing_shampoo",
        "linha": "So Pure",
        "nome": "So Pure Energizing Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["250ml", "1000ml"],
        "preco_250ml": 139.00,
        "publico": "B2C+B2B",
        "indicado_para": ["queda capilar leve", "fortalecimento do bulbo"],
        "selo": "94% natural / vegano",
        "beneficios": ["estimula o couro cabeludo", "tonifica os fios", "uso diário"],
        "ingredientes_destaque": ["óleo essencial de hortelã-pimenta", "alecrim"],
    },
    "sopure_color_care": {
        "id": "sopure_color_care",
        "linha": "So Pure",
        "nome": "So Pure Color Care Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["250ml", "1000ml"],
        "preco_250ml": 139.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo colorido", "fios químicos", "manutenção de cor"],
        "selo": "94% natural / vegano",
        "beneficios": ["prolonga duração da coloração", "limpeza suave para fios com química"],
    },

    # ─────────── LINHA STYLE ───────────
    "style_liquid_definer": {
        "id": "style_liquid_definer",
        "linha": "Style",
        "nome": "Liquid Definer",
        "tipo": "modelador/cremoso",
        "tamanhos": ["140ml"],
        "preco": 99.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cachos", "ondulados", "definição sem volume"],
        "beneficios": ["define cachos com leveza", "controle de frizz", "fixação flexível"],
    },
    "style_defining_lotion": {
        "id": "style_defining_lotion",
        "linha": "Style",
        "nome": "Defining Lotion",
        "tipo": "loção modeladora",
        "tamanhos": ["200ml"],
        "preco": 89.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo liso e ondulado", "escova", "babyliss"],
        "beneficios": ["base para finalização", "proteção térmica", "memória de forma"],
    },

    # ─────────── LINHA COLOR (B2B / profissional) ───────────
    "color_tinta_color": {
        "id": "color_tinta_color",
        "linha": "Color",
        "nome": "Tinta Color",
        "tipo": "coloração permanente",
        "tamanhos": ["60ml"],
        "preco_b2b": 39.90,
        "publico": "B2B",
        "indicado_para": ["coloração profissional em salão"],
        "observacao": "Mais de 100 nuances. Requer revelador Keune (3%, 6%, 9%, 12%). Uso profissional apenas.",
    },
    "color_so_pure_color": {
        "id": "color_so_pure_color",
        "linha": "Color",
        "nome": "So Pure Color",
        "tipo": "coloração com ingredientes naturais",
        "tamanhos": ["60ml"],
        "preco_b2b": 49.90,
        "publico": "B2B",
        "indicado_para": ["clientes que buscam coloração com menor agressão"],
        "observacao": "Formulação com ingredientes naturais. Uso profissional.",
    },

    # ─────────── LINHA MAN ───────────
    "man_refreshing_shampoo": {
        "id": "man_refreshing_shampoo",
        "linha": "Man",
        "nome": "Refreshing Shampoo",
        "tipo": "shampoo masculino",
        "tamanhos": ["250ml"],
        "preco": 89.00,
        "publico": "B2C+B2B",
        "indicado_para": ["uso diário masculino", "couro cabeludo oleoso", "sensação refrescante"],
        "beneficios": ["limpeza profunda sem ressecar", "frescor mentolado"],
    },
    "man_texture_cream": {
        "id": "man_texture_cream",
        "linha": "Man",
        "nome": "Texture Cream",
        "tipo": "modelador masculino",
        "tamanhos": ["100ml"],
        "preco": 109.00,
        "publico": "B2C+B2B",
        "indicado_para": ["modelagem masculina", "fixação média", "acabamento matte"],
        "beneficios": ["textura para penteado", "sem brilho", "fácil de manusear"],
    },

    # ─────────── LINHA BLEND (Cacheados e Crespos) ───────────
    "blend_curls_shampoo": {
        "id": "blend_curls_shampoo",
        "linha": "Blend",
        "nome": "Blend Curls Shampoo",
        "tipo": "shampoo",
        "tamanhos": ["300ml"],
        "preco": 129.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo cacheado", "crespo", "transição capilar"],
        "tipo_fio": ["cacheado", "crespo"],
        "beneficios": ["respeita curvatura natural", "hidratação dos cachos", "definição"],
    },
    "blend_curl_defining": {
        "id": "blend_curl_defining",
        "linha": "Blend",
        "nome": "Curl Defining Cream",
        "tipo": "creme de pentear",
        "tamanhos": ["200ml"],
        "preco": 109.00,
        "publico": "B2C+B2B",
        "indicado_para": ["cabelo cacheado", "crespo", "low-poo/no-poo"],
        "beneficios": ["definição duradoura", "anti-frizz", "leveza"],
    },
}


# Kits recomendados por perfil — usado pelo pitch para sugerir combos
KEUNE_KITS_RECOMENDADOS = {
    "seco_quimica": {
        "perfil": "Cabelo seco, com química (progressiva, coloração, descoloração)",
        "linha": "Care — Keratin Smooth + Vital Nutrition",
        "produtos": ["care_keratin_smooth_shampoo", "care_vital_nutrition_conditioner", "care_vital_nutrition_mask", "care_satin_oil"],
    },
    "cacheado_definicao": {
        "perfil": "Cacheados ou crespos buscando definição",
        "linha": "Blend",
        "produtos": ["blend_curls_shampoo", "blend_curl_defining", "style_liquid_definer"],
    },
    "couro_sensivel": {
        "perfil": "Couro cabeludo sensível, uso diário",
        "linha": "So Pure Calming",
        "produtos": ["sopure_calming_shampoo", "care_vital_nutrition_conditioner"],
    },
    "queda_fortalecimento": {
        "perfil": "Queda leve, busca fortalecimento",
        "linha": "So Pure Energizing",
        "produtos": ["sopure_energizing_shampoo"],
        "observacao": "Para queda intensa, encaminhar para dermatologista antes",
    },
    "colorido_manutencao": {
        "perfil": "Cabelo colorido buscando manutenção da cor",
        "linha": "So Pure Color Care",
        "produtos": ["sopure_color_care", "care_vital_nutrition_mask"],
    },
    "masculino_diario": {
        "perfil": "Cuidado masculino diário",
        "linha": "Man",
        "produtos": ["man_refreshing_shampoo", "man_texture_cream"],
    },
}


def buscar_produtos(
    linha: str | None = None,
    publico: str | None = None,
    tipo: str | None = None,
    indicacao: str | None = None,
) -> list[dict]:
    """Filtra o catálogo por critério. Usado pela tool `consultar_catalogo_keune`."""
    resultados = []
    for prod in KEUNE_CATALOG.values():
        if linha and prod["linha"].lower() != linha.lower():
            continue
        if publico and publico not in prod.get("publico", ""):
            continue
        if tipo and prod.get("tipo", "").lower() != tipo.lower():
            continue
        if indicacao:
            indicacoes = [i.lower() for i in prod.get("indicado_para", [])]
            if not any(indicacao.lower() in i for i in indicacoes):
                continue
        resultados.append(prod)
    return resultados


def recomendar_kit(perfil_key: str) -> dict | None:
    """Retorna kit completo com produtos expandidos a partir de uma chave de perfil."""
    kit = KEUNE_KITS_RECOMENDADOS.get(perfil_key)
    if not kit:
        return None
    return {
        "perfil": kit["perfil"],
        "linha": kit["linha"],
        "observacao": kit.get("observacao"),
        "produtos": [KEUNE_CATALOG[pid] for pid in kit["produtos"] if pid in KEUNE_CATALOG],
    }
