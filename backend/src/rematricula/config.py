from datetime import date
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"

    # Chave curta enfraquece o HS256; RFC 7518 pede no minimo 32 bytes.
    jwt_secret: str = Field(min_length=32)
    jwt_expira_minutos: int = 30
    # NoDecode: sem isso o pydantic-settings tenta json.loads no valor do ambiente e
    # quebra com uma lista separada por virgula.
    cors_origens: Annotated[list[str], NoDecode] = Field(default_factory=list)

    ano_letivo_alvo: int = 2027
    desconto_valido_ate: date = date(2027, 1, 31)
    link_waba: str = ""

    motherduck_token: str = ""
    motherduck_database: str = ""

    # Ids de servico no sistema de gestao. Filtrar por id, nunca por nome: ha
    # servicos inativos homonimos que ainda aparecem em titulos antigos.
    servico_ids_matricula: list[int] = Field(default_factory=lambda: [1001, 1002])
    servico_ids_material: list[int] = Field(default_factory=lambda: [2001])

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    # Content Template aprovado pela Meta, com uma unica variavel: o codigo.
    twilio_content_sid_otp: str = ""

    # Segredo proprio do OTP: separado do JWT para que vazar um nao comprometa o outro.
    otp_segredo: str = ""
    otp_digitos: int = 6
    otp_validade_minutos: int = 10
    otp_max_tentativas: int = 5
    otp_max_envios: int = 3
    firestore_colecao_tentativas: str = "otp_tentativas"
    twilio_verify_service_sid: str = ""

    # Sem projeto explicito o storage.Client() sonda o metadata server do GCE e
    # leva ~25s para subir fora do GCP.
    gcp_project: str = ""
    gcs_bucket_boletos: str = ""
    gcs_prefixo_matricula: str = ""
    gcs_prefixo_material: str = ""

    @field_validator("cors_origens", mode="before")
    @classmethod
    def _aceita_lista_separada_por_virgula(cls, valor: object) -> object:
        if isinstance(valor, str):
            return [origem.strip() for origem in valor.split(",") if origem.strip()]
        return valor


@lru_cache
def obter_config() -> Config:
    return Config()  # type: ignore[call-arg]  # os campos vem do ambiente / .env
