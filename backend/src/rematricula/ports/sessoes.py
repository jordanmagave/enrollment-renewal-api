from datetime import datetime
from typing import Protocol

from rematricula.domain.modelos import Sessao, SessaoEmitida


class Sessoes(Protocol):
    def emitir(
        self,
        responsavel_ids: tuple[str, ...],
        cpf_hash: str,
        matriculas: tuple[str, ...],
        agora: datetime | None = None,
    ) -> SessaoEmitida: ...

    def validar(self, token: str) -> Sessao:
        """Levanta SessaoInvalida se o token estiver ausente, adulterado ou expirado."""
        ...
