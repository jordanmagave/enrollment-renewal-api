from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rematricula.api import rotas_auth, rotas_titulos
from rematricula.api.dependencias import Dependencias
from rematricula.api.erros import registrar_tratadores
from rematricula.api.log import configurar_log, registrar_middleware_de_log
from rematricula.config import Config, obter_config

PREFIXO_API = "/api/v1"


def criar_app(dependencias: Dependencias, config: Config | None = None) -> FastAPI:
    app = FastAPI(
        title="Enrollment Renewal API",
        version="0.1.0",
        docs_url="/docs",
    )

    if config and config.cors_origens:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origens,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
        )

    registrar_middleware_de_log(app)
    registrar_tratadores(app, link_waba=dependencias.link_waba)
    app.include_router(rotas_auth.criar_router(dependencias), prefix=PREFIXO_API)
    app.include_router(rotas_titulos.criar_router(dependencias), prefix=PREFIXO_API)

    @app.get("/health", tags=["infra"])
    def health() -> dict[str, Any]:
        return {"status": "ok"}

    return app


def montar_app() -> FastAPI:
    configurar_log()
    config = obter_config()
    return criar_app(Dependencias.de_config(config), config)
