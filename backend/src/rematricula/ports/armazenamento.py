from dataclasses import dataclass
from typing import IO, Protocol

from rematricula.domain.modelos import Servico


@dataclass(frozen=True, slots=True)
class BoletoPdf:
    nome_arquivo: str
    conteudo: IO[bytes]


class ArmazenamentoBoletos(Protocol):
    """Pasta de boletos ja emitidos. Matricula e material didatico ficam em pastas separadas."""

    def abrir(self, servico: Servico, matricula: str) -> BoletoPdf | None: ...

    def existe(self, servico: Servico, matricula: str) -> bool: ...
