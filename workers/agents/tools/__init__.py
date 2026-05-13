from workers.agents.tools.catalog import (
    calcular_frete,
    consultar_catalogo,
    verificar_estoque,
)
from workers.agents.tools.crm import (
    buscar_cliente,
    criar_oportunidade,
    registrar_lead,
)
from workers.agents.tools.handoff import agendar_followup, transferir_humano

ALL_TOOLS = [
    consultar_catalogo,
    verificar_estoque,
    calcular_frete,
    buscar_cliente,
    registrar_lead,
    criar_oportunidade,
    transferir_humano,
    agendar_followup,
]

__all__ = [
    "ALL_TOOLS",
    "consultar_catalogo",
    "verificar_estoque",
    "calcular_frete",
    "buscar_cliente",
    "registrar_lead",
    "criar_oportunidade",
    "transferir_humano",
    "agendar_followup",
]
