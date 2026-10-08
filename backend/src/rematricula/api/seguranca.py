from collections.abc import Callable

from fastapi import Request

from rematricula.domain.erros import SessaoInvalida
from rematricula.domain.modelos import Sessao
from rematricula.ports.sessoes import Sessoes

_PREFIXO = "Bearer "


def criar_dependencia_de_sessao(sessoes: Sessoes) -> Callable[[Request], Sessao]:
    """Transforma o header Authorization em Sessao; recusa qualquer token invalido."""

    def dependencia(request: Request) -> Sessao:
        cabecalho = request.headers.get("Authorization", "")
        if not cabecalho.startswith(_PREFIXO):
            raise SessaoInvalida("Sessao invalida ou expirada")

        return sessoes.validar(cabecalho.removeprefix(_PREFIXO).strip())

    return dependencia
