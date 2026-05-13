"""
Tools específicas Keune — sobrescrevem o catálogo genérico
com produtos reais da marca e adicionam FAQ + diagnóstico.
"""
from typing import Any, Literal

import structlog
from langchain_core.tools import tool

from workers.agents.configs.keune.catalog import (
    KEUNE_CATALOG,
    buscar_produtos,
    recomendar_kit,
)
from workers.agents.configs.keune.knowledge import (
    REPRESENTANTES_REGIONAIS,
    consultar_faq,
    sugerir_linhas_por_queixa,
)

log = structlog.get_logger()


@tool
def consultar_catalogo_keune(
    linha: str | None = None,
    publico: Literal["B2C", "B2B"] | None = None,
    tipo: str | None = None,
    indicacao: str | None = None,
) -> list[dict[str, Any]]:
    """
    Busca produtos no catálogo oficial Keune Brasil.

    Args:
        linha: Care, So Pure, Style, Color, Man ou Blend
        publico: B2C (consumidor) ou B2B (profissional)
        tipo: shampoo, condicionador, mascara, leave-in, etc
        indicacao: descrição da queixa do cliente (ex: "cabelo seco", "frizz", "cachos")

    Returns:
        Lista de produtos com nome, preço, benefícios, modo de uso e ingredientes
    """
    log.info("keune.catalog_search", linha=linha, publico=publico, indicacao=indicacao)
    resultados = buscar_produtos(linha=linha, publico=publico, tipo=tipo, indicacao=indicacao)
    return resultados[:5]


@tool
def recomendar_kit_keune(perfil: str) -> dict[str, Any] | None:
    """
    Retorna kit completo Keune baseado no perfil capilar do cliente.

    Perfis disponíveis:
    - seco_quimica: cabelo seco com química (progressiva, coloração, descoloração)
    - cacheado_definicao: cacheados ou crespos buscando definição
    - couro_sensivel: couro cabeludo sensível, uso diário
    - queda_fortalecimento: queda leve, fortalecimento
    - colorido_manutencao: cabelo colorido, manutenção de cor
    - masculino_diario: cuidado masculino diário

    Args:
        perfil: chave do perfil identificado no diagnóstico

    Returns:
        Dict com linha, lista de produtos do kit, observações
    """
    log.info("keune.kit_recommendation", perfil=perfil)
    return recomendar_kit(perfil)


@tool
def consultar_faq_keune(pergunta: str) -> dict[str, str] | None:
    """
    Consulta FAQ oficial Keune. Use SEMPRE antes de responder perguntas sobre:
    - Onde comprar
    - Veganismo / cruelty-free
    - Diferenciais da marca
    - Uso após progressiva/química
    - Cabelo oleoso, seco, queda, etc.

    Args:
        pergunta: termo de busca ou pergunta do cliente

    Returns:
        Dict com pergunta e resposta oficial; "HANDOFF" se pergunta exige humano
    """
    log.info("keune.faq_lookup", pergunta=pergunta[:60])
    return consultar_faq(pergunta)


@tool
def diagnosticar_queixa(queixa: str) -> list[str]:
    """
    Mapeia queixa capilar do cliente para linhas Keune indicadas.

    Args:
        queixa: ressecamento, frizz, queda, oleosidade, couro_sensivel,
                volume_excessivo, falta_definicao_cachos, cor_desbotando, danificado_quimica

    Returns:
        Lista de linhas Keune recomendadas (em ordem de prioridade)
    """
    log.info("keune.diagnose", queixa=queixa)
    return sugerir_linhas_por_queixa(queixa)


@tool
def conectar_representante(
    regiao: Literal["sudeste", "sul", "nordeste", "norte", "centro_oeste"],
    nome_profissional: str,
    estabelecimento: str,
    cidade: str,
    interesse: str,
) -> dict[str, Any]:
    """
    Conecta cabeleireiro/salão com representante Keune regional.
    Use SEMPRE quando identificar um cliente profissional (B2B) qualificado.

    Args:
        regiao: região do Brasil do profissional
        nome_profissional: nome do cabeleireiro/proprietário
        estabelecimento: nome do salão/distribuidora
        cidade: cidade onde atende
        interesse: linhas de interesse (ex: "Color, So Pure")

    Returns:
        Dict com nome do representante, tempo de resposta esperado, ticket_id
    """
    rep = REPRESENTANTES_REGIONAIS.get(regiao, REPRESENTANTES_REGIONAIS["sudeste"])
    log.info(
        "keune.b2b_handoff",
        regiao=regiao,
        estabelecimento=estabelecimento,
        cidade=cidade,
    )
    return {
        "representante": rep["nome"],
        "tempo_resposta": rep["tempo_resposta"],
        "ticket_id": f"KEUNE-B2B-{hash(nome_profissional + estabelecimento) % 100000:05d}",
        "proximos_passos": "O representante entra em contato para envio de tabela profissional + amostras.",
    }


@tool
def localizar_salao_parceiro(cidade: str, bairro: str | None = None) -> list[dict[str, Any]]:
    """
    Localiza salões parceiros Keune próximos ao cliente B2C.
    Use quando o cliente perguntar onde comprar ou encontrar a marca presencialmente.

    Args:
        cidade: cidade do cliente
        bairro: bairro (opcional)

    Returns:
        Lista de salões parceiros com nome, endereço e telefone
    """
    log.info("keune.salon_locator", cidade=cidade, bairro=bairro)
    # TODO: integrar com base real de salões parceiros
    return [
        {
            "nome": f"Salão demonstrativo em {cidade}",
            "endereco": f"Endereço exemplo - {bairro or 'centro'}",
            "telefone": "(00) 0000-0000",
            "linhas_disponiveis": ["Care", "So Pure", "Style"],
        }
    ]


KEUNE_TOOLS = [
    consultar_catalogo_keune,
    recomendar_kit_keune,
    consultar_faq_keune,
    diagnosticar_queixa,
    conectar_representante,
    localizar_salao_parceiro,
]
