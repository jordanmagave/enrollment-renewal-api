import pytest
from fastapi.testclient import TestClient

from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.api.main import criar_app
from tests.conftest import CPF_RESPONSAVEL, CPF_SEM_CADASTRO

LINK_WABA = "https://wa.me/5591999999999"


@pytest.fixture
def cliente(repositorio: RepositorioEmMemoria, otp: OtpFake) -> TestClient:
    from rematricula.api.dependencias import Dependencias

    return TestClient(
        criar_app(Dependencias.para_teste(repositorio=repositorio, otp=otp, link_waba=LINK_WABA))
    )


def test_iniciar_devolve_o_telefone_mascarado(cliente: TestClient, otp: OtpFake) -> None:
    resposta = cliente.post("/api/v1/auth/iniciar", json={"cpf": CPF_RESPONSAVEL})

    assert resposta.status_code == 200
    assert resposta.json() == {"telefone_mascarado": "(91) ****-7777"}
    assert otp.envios == ["+5591988887777"]


def test_iniciar_com_cpf_invalido_recusa_sem_chamar_o_otp(
    cliente: TestClient, otp: OtpFake
) -> None:
    resposta = cliente.post("/api/v1/auth/iniciar", json={"cpf": "123"})

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "cpf_invalido"
    assert otp.envios == []


def test_iniciar_com_cpf_sem_cadastro_orienta_a_falar_com_a_escola(cliente: TestClient) -> None:
    resposta = cliente.post("/api/v1/auth/iniciar", json={"cpf": CPF_SEM_CADASTRO})

    corpo = resposta.json()
    assert resposta.status_code == 404
    assert corpo["codigo"] == "responsavel_nao_encontrado"
    assert corpo["link_suporte"] == LINK_WABA


def test_verificar_com_codigo_correto_devolve_token(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"}
    )

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["token_type"] == "bearer"
    assert corpo["expires_in"] == 1800
    assert corpo["access_token"]


def test_verificar_com_codigo_errado_orienta_a_falar_com_a_escola(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "999999"}
    )

    corpo = resposta.json()
    assert resposta.status_code == 401
    assert corpo["codigo"] == "codigo_invalido"
    assert corpo["link_suporte"] == LINK_WABA


def test_resposta_de_erro_nunca_devolve_o_cpf(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "999999"}
    )

    assert "52998224725" not in resposta.text
    assert CPF_RESPONSAVEL not in resposta.text
