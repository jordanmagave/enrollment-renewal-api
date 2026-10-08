from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class IniciarAutenticacaoPedido(BaseModel):
    cpf: str = Field(max_length=20)


class IniciarAutenticacaoResposta(BaseModel):
    telefone_mascarado: str


class VerificarCodigoPedido(BaseModel):
    cpf: str = Field(max_length=20)
    codigo: str = Field(max_length=10)


class VerificarCodigoResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 — nome do esquema OAuth, nao um segredo
    expires_in: int


class TituloItem(BaseModel):
    matricula: str
    nome_aluno: str
    turma: str
    valor_original: Decimal
    desconto: Decimal
    valor_com_desconto: Decimal
    boleto_disponivel: bool


class ListaTitulosResposta(BaseModel):
    ano_letivo: int
    desconto_valido_ate: date
    dias_restantes: int
    desconto_vigente: bool
    total_original: Decimal
    total_com_desconto: Decimal
    economia_total: Decimal
    itens: list[TituloItem]


class ErroResposta(BaseModel):
    codigo: str
    mensagem: str
    link_suporte: str = ""
