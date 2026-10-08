from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from rematricula.domain.erros import (
    AlunoNaoAutorizado,
    BoletoIndisponivel,
    CodigoInvalido,
    CpfInvalido,
    ErroDeDominio,
    ResponsavelNaoEncontrado,
    SessaoInvalida,
    TelefoneInvalido,
    TentativasExcedidas,
)

# Cada erro de dominio vira status HTTP + codigo estavel para o front tratar.
_MAPA: dict[type[ErroDeDominio], tuple[int, str]] = {
    CpfInvalido: (status.HTTP_400_BAD_REQUEST, "cpf_invalido"),
    TelefoneInvalido: (status.HTTP_400_BAD_REQUEST, "telefone_invalido"),
    ResponsavelNaoEncontrado: (status.HTTP_404_NOT_FOUND, "responsavel_nao_encontrado"),
    CodigoInvalido: (status.HTTP_401_UNAUTHORIZED, "codigo_invalido"),
    TentativasExcedidas: (status.HTTP_429_TOO_MANY_REQUESTS, "tentativas_excedidas"),
    SessaoInvalida: (status.HTTP_401_UNAUTHORIZED, "sessao_invalida"),
    AlunoNaoAutorizado: (status.HTTP_403_FORBIDDEN, "aluno_nao_autorizado"),
    BoletoIndisponivel: (status.HTTP_404_NOT_FOUND, "boleto_indisponivel"),
}

_PADRAO = (status.HTTP_400_BAD_REQUEST, "erro_de_dominio")


def registrar_tratadores(app: FastAPI, link_waba: str) -> None:
    @app.exception_handler(ErroDeDominio)
    async def _tratar(_: Request, erro: Exception) -> JSONResponse:
        http_status, codigo = (
            _MAPA.get(type(erro), _PADRAO) if isinstance(erro, ErroDeDominio) else _PADRAO
        )
        return JSONResponse(
            status_code=http_status,
            content={"codigo": codigo, "mensagem": str(erro), "link_suporte": link_waba},
        )
