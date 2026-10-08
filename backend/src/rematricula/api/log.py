import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import IO, Any

from fastapi import FastAPI, Request, Response

_LOGGER = "rematricula"

# O Cloud Logging le "severity"; sem isso tudo cai como texto sem nivel.
_CAMPOS_EXTRA = "dados"


class FormatadorJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        registro: dict[str, Any] = {
            "severity": record.levelname,
            "mensagem": record.getMessage(),
        }
        registro.update(getattr(record, _CAMPOS_EXTRA, {}))

        if record.exc_info:
            registro["excecao"] = self.formatException(record.exc_info)

        return json.dumps(registro, ensure_ascii=False)


def configurar_log(destino: IO[str] | None = None) -> logging.Logger:
    manipulador = logging.StreamHandler(destino) if destino else logging.StreamHandler()
    manipulador.setFormatter(FormatadorJson())

    logger = logging.getLogger(_LOGGER)
    logger.handlers = [manipulador]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _severidade(status: int) -> int:
    if status >= 500:
        return logging.ERROR
    if status >= 400:
        return logging.WARNING
    return logging.INFO


def _rota(request: Request) -> str:
    """Template da rota, nunca o caminho real: a matricula na URL identifica um aluno.

    O template e montado trocando cada valor de path param pelo nome dele. Assim o
    prefixo do router entra (o `scope["route"]` desta versao do FastAPI vem sem ele)
    e a troca do valor concreto fica garantida.
    """
    if request.scope.get("route") is None:
        return "desconhecida"

    caminho = request.url.path
    for nome, valor in (request.scope.get("path_params") or {}).items():
        caminho = caminho.replace(str(valor), "{" + nome + "}")
    return caminho


def registrar_middleware_de_log(app: FastAPI) -> None:
    logger = logging.getLogger(_LOGGER)

    @app.middleware("http")
    async def _registrar(
        request: Request, seguir: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        inicio = time.perf_counter()
        resposta = await seguir(request)
        duracao = (time.perf_counter() - inicio) * 1000

        # Nunca logamos corpo, query string, cabecalhos nem o caminho concreto:
        # todos carregam CPF, telefone, token ou matricula.
        logger.log(
            _severidade(resposta.status_code),
            "requisicao",
            extra={
                _CAMPOS_EXTRA: {
                    "metodo": request.method,
                    "rota": _rota(request),
                    "status": resposta.status_code,
                    "duracao_ms": round(duracao, 1),
                }
            },
        )
        return resposta
