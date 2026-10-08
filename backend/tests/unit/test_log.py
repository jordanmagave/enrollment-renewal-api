import json
import logging
from io import StringIO

import pytest
from fastapi.testclient import TestClient

from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.api.dependencias import Dependencias
from rematricula.api.log import FormatadorJson, configurar_log
from rematricula.api.main import criar_app
from tests.conftest import CPF_RESPONSAVEL


@pytest.fixture
def saida() -> StringIO:
    fluxo = StringIO()
    configurar_log(destino=fluxo)
    return fluxo


@pytest.fixture
def cliente(repositorio: RepositorioEmMemoria, otp: OtpFake) -> TestClient:
    return TestClient(criar_app(Dependencias.para_teste(repositorio=repositorio, otp=otp)))


def linhas(saida: StringIO) -> list[dict[str, object]]:
    return [json.loads(linha) for linha in saida.getvalue().splitlines() if linha.strip()]


def test_cada_requisicao_vira_uma_linha_json(cliente: TestClient, saida: StringIO) -> None:
    cliente.get("/health")

    (registro,) = linhas(saida)
    assert registro["metodo"] == "GET"
    assert registro["rota"] == "/health"
    assert registro["status"] == 200
    assert isinstance(registro["duracao_ms"], int | float)


def test_usa_o_campo_severity_que_o_cloud_logging_espera(
    cliente: TestClient, saida: StringIO
) -> None:
    cliente.get("/health")

    assert linhas(saida)[0]["severity"] == "INFO"


def test_erro_do_cliente_sai_como_warning(cliente: TestClient, saida: StringIO) -> None:
    cliente.post("/api/v1/auth/iniciar", json={"cpf": "123"})

    assert linhas(saida)[0]["severity"] == "WARNING"


def test_cpf_enviado_no_corpo_nunca_aparece_no_log(cliente: TestClient, saida: StringIO) -> None:
    cliente.post("/api/v1/auth/iniciar", json={"cpf": CPF_RESPONSAVEL})

    texto = saida.getvalue()
    assert "52998224725" not in texto
    assert CPF_RESPONSAVEL not in texto


def test_telefone_nunca_aparece_no_log(cliente: TestClient, saida: StringIO) -> None:
    cliente.post("/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"})

    assert "988887777" not in saida.getvalue()


def test_token_de_sessao_nunca_aparece_no_log(cliente: TestClient, saida: StringIO) -> None:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"}
    )
    token = resposta.json()["access_token"]
    cliente.get("/api/v1/matriculas", headers={"Authorization": f"Bearer {token}"})

    assert token not in saida.getvalue()


def test_matricula_na_url_nao_vaza_para_o_log(cliente: TestClient, saida: StringIO) -> None:
    """A rota e logada como template, sem o valor — matricula identifica um aluno."""
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"}
    )
    token = resposta.json()["access_token"]
    cliente.get("/api/v1/matriculas/100001/boleto", headers={"Authorization": f"Bearer {token}"})

    registro = linhas(saida)[-1]
    assert registro["rota"] == "/api/v1/matriculas/{matricula}/boleto"
    assert "100001" not in saida.getvalue()


def test_formatador_serializa_excecao_sem_quebrar() -> None:
    formatador = FormatadorJson()
    registro = logging.LogRecord(
        name="teste",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="falhou",
        args=(),
        exc_info=None,
    )

    assert json.loads(formatador.format(registro))["severity"] == "ERROR"
