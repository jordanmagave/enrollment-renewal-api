import pytest
from fastapi.testclient import TestClient

from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.api.dependencias import Dependencias
from rematricula.api.main import criar_app
from tests.conftest import CPF_RESPONSAVEL


@pytest.fixture
def cliente(repositorio: RepositorioEmMemoria, otp: OtpFake) -> TestClient:
    return TestClient(criar_app(Dependencias.para_teste(repositorio=repositorio, otp=otp)))


@pytest.fixture
def autorizacao(cliente: TestClient) -> dict[str, str]:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"}
    )
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_lista_matriculas_com_valores_e_prazo_da_campanha(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    resposta = cliente.get("/api/v1/matriculas", headers=autorizacao)

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["ano_letivo"] == 2027
    assert corpo["desconto_valido_ate"] == "2027-01-31"
    assert corpo["economia_total"] == "400.00"
    assert corpo["itens"][0] == {
        "matricula": "100001",
        "nome_aluno": "ANA BEATRIZ SOUZA LIMA",
        "turma": "1.FD1.3A.T01",
        "valor_original": "1000.00",
        "desconto": "200.00",
        "valor_com_desconto": "800.00",
        "boleto_disponivel": False,
    }


def test_lista_material_didatico_separadamente(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    resposta = cliente.get("/api/v1/material-didatico", headers=autorizacao)

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert [item["matricula"] for item in corpo["itens"]] == ["100001"]


@pytest.mark.parametrize("rota", ["/api/v1/matriculas", "/api/v1/material-didatico"])
def test_sem_token_nao_lista_nada(cliente: TestClient, rota: str) -> None:
    resposta = cliente.get(rota)

    assert resposta.status_code == 401


@pytest.mark.parametrize("rota", ["/api/v1/matriculas", "/api/v1/material-didatico"])
def test_token_adulterado_e_recusado(cliente: TestClient, rota: str) -> None:
    resposta = cliente.get(rota, headers={"Authorization": "Bearer nao.e.um.token"})

    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "sessao_invalida"
