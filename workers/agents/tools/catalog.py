"""Tools de catálogo — consulta produtos, preços, estoque."""
from typing import Any
from langchain_core.tools import tool
import structlog

log = structlog.get_logger()


@tool
def consultar_catalogo(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """
    Busca produtos no catálogo por nome, categoria ou características.

    Args:
        query: Termo de busca (ex: "iPhone 15", "notebook gamer", "café premium")
        max_results: Quantidade máxima de produtos a retornar (1-5)

    Returns:
        Lista de produtos com: id, nome, preço, estoque, descrição, características
    """
    log.info("tool.catalog_search", query=query)
    # TODO: substituir por consulta real ao banco de produtos
    return [
        {
            "id": "PROD-001",
            "nome": f"Produto demo para '{query}'",
            "preco": 299.90,
            "estoque": 12,
            "descricao": "Descrição vinda do banco de produtos.",
            "caracteristicas": ["caracteristica 1", "caracteristica 2"],
        }
    ][:max_results]


@tool
def verificar_estoque(product_id: str) -> dict[str, Any]:
    """
    Verifica estoque em tempo real de um produto específico.

    Args:
        product_id: ID do produto

    Returns:
        Dict com: product_id, quantidade_disponivel, prazo_reposicao (se zerado)
    """
    log.info("tool.stock_check", product_id=product_id)
    return {
        "product_id": product_id,
        "quantidade_disponivel": 10,
        "prazo_reposicao": None,
    }


@tool
def calcular_frete(cep: str, product_ids: list[str]) -> dict[str, Any]:
    """
    Calcula frete e prazo de entrega para um CEP.

    Args:
        cep: CEP de destino (apenas dígitos)
        product_ids: Lista de IDs dos produtos do pedido

    Returns:
        Dict com: valor, prazo_dias, transportadora
    """
    log.info("tool.shipping_calc", cep=cep, products=len(product_ids))
    return {
        "valor": 19.90,
        "prazo_dias": 5,
        "transportadora": "Correios PAC",
    }
