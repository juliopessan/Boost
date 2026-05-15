"""
Gestão segura de credenciais para o SDR WhatsApp.

Estratégia em 3 camadas (ordem de prioridade):
  1. AWS Secrets Manager (produção)
  2. AWS Systems Manager Parameter Store (staging)
  3. Variáveis de ambiente / arquivo .env (desenvolvimento local)

Uso:
    from secrets import get_secret
    api_key = get_secret("EVOLUTION_API_KEY")

Em produção setar:
    SECRETS_BACKEND=aws_secrets_manager
    AWS_SECRETS_PREFIX=boost/sdr/  # opcional

Em desenvolvimento: o backend default lê só do os.environ
(que o uvicorn já carrega do .env via python-dotenv).
"""

import logging
import os
from functools import lru_cache
from typing import Literal

log = logging.getLogger(__name__)

SecretsBackend = Literal["env", "aws_secrets_manager", "aws_parameter_store"]


def _get_backend() -> SecretsBackend:
    return os.environ.get("SECRETS_BACKEND", "env").lower()  # type: ignore[return-value]


@lru_cache(maxsize=128)
def get_secret(name: str, required: bool = True) -> str:
    """
    Recupera uma credencial pelo nome lógico.

    Args:
        name: Nome da credencial (ex: "EVOLUTION_API_KEY")
        required: Se True, levanta RuntimeError quando não encontrar

    Returns:
        Valor da credencial como string

    Raises:
        RuntimeError: se required=True e credencial não existir
    """
    backend = _get_backend()

    try:
        if backend == "aws_secrets_manager":
            value = _from_aws_secrets_manager(name)
        elif backend == "aws_parameter_store":
            value = _from_parameter_store(name)
        else:
            value = os.environ.get(name)
    except Exception as e:
        log.warning(
            "secrets.backend_failure_falling_back_to_env",
            extra={"backend": backend, "name": name, "error": str(e)[:120]},
        )
        value = os.environ.get(name)

    if not value:
        if required:
            raise RuntimeError(
                f"Credencial '{name}' não encontrada (backend={backend}). "
                f"Verifique seu .env local ou o secret manager."
            )
        return ""

    return value


# ─────────── BACKENDS ───────────


def _from_aws_secrets_manager(name: str) -> str | None:
    """Lê secret do AWS Secrets Manager (recomendado para produção)."""
    import boto3  # lazy import

    prefix = os.environ.get("AWS_SECRETS_PREFIX", "boost/sdr/")
    secret_id = f"{prefix}{name}"

    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    response = client.get_secret_value(SecretId=secret_id)
    return response.get("SecretString")


def _from_parameter_store(name: str) -> str | None:
    """Lê secret do AWS Systems Manager Parameter Store (alternativa mais barata)."""
    import boto3  # lazy import

    prefix = os.environ.get("AWS_PARAMETERS_PREFIX", "/boost/sdr/")
    parameter_name = f"{prefix}{name}"

    client = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    response = client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response.get("Parameter", {}).get("Value")


# ─────────── MASK ───────────


def mask_secret(value: str, show_last: int = 4) -> str:
    """Mascara valor para logging seguro: 'abc...XYZW' (mostra últimos N chars)."""
    if not value:
        return "<empty>"
    if len(value) <= show_last:
        return "*" * len(value)
    return f"{'*' * (len(value) - show_last)}{value[-show_last:]}"
