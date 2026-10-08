from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from rematricula.domain.cpf import Cpf
from rematricula.domain.telefone import Telefone


class Servico(StrEnum):
    """Etapas da jornada. Os ids de servico correspondentes ficam em `config`."""

    MATRICULA = "matricula"
    MATERIAL_DIDATICO = "material_didatico"


@dataclass(frozen=True, slots=True)
class Responsavel:
    """O mesmo CPF pode aparecer em varios registros de responsavel, entao `ids` e uma lista."""

    ids: tuple[str, ...]
    nome: str
    cpf: Cpf
    telefone: Telefone


@dataclass(frozen=True, slots=True)
class Aluno:
    matricula: str
    nome: str
    turma: str


@dataclass(frozen=True, slots=True)
class Sessao:
    responsavel_ids: tuple[str, ...]
    cpf_hash: str
    matriculas: tuple[str, ...]

    def autoriza(self, matricula: str) -> bool:
        return matricula in self.matriculas


@dataclass(frozen=True, slots=True)
class SessaoEmitida:
    token: str
    expira_em_segundos: int


@dataclass(frozen=True, slots=True)
class Titulo:
    aluno: Aluno
    servico: Servico
    valor_original: Decimal
    valor_com_desconto: Decimal
    vencimento: date | None = None
    desconto_valido_ate: date | None = None

    @property
    def desconto(self) -> Decimal:
        return self.valor_original - self.valor_com_desconto
