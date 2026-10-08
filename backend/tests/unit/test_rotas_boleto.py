import pytest
from fastapi.testclient import TestClient

from rematricula.adapters.fakes.armazenamento import ArmazenamentoEmMemoria
from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.api.dependencias import Dependencias
from rematricula.api.main import criar_app
from rematricula.domain.modelos import Servico
from tests.conftest import CPF_OUTRO_RESPONSAVEL, CPF_RESPONSAVEL


@pytest.fixture
def armazenamento() -> ArmazenamentoEmMemoria:
    armazenamento = ArmazenamentoEmMemoria()
    armazenamento.adicionar(
        Servico.MATRICULA,
        matricula="100001",
        nome_arquivo="100001-ANA BEATRIZ SOUZA LIMA.pdf",
        conteudo=b"%PDF-1.4 matricula",
    )
    armazenamento.adicionar(
        Servico.MATERIAL_DIDATICO,
        matricula="100001",
        nome_arquivo="100001-ANA BEATRIZ SOUZA LIMA.pdf",
        conteudo=b"%PDF-1.4 material",
    )
    return armazenamento


@pytest.fixture
def cliente(
    repositorio: RepositorioEmMemoria, otp: OtpFake, armazenamento: ArmazenamentoEmMemoria
) -> TestClient:
    return TestClient(
        criar_app(
            Dependencias.para_teste(repositorio=repositorio, otp=otp, armazenamento=armazenamento)
        )
    )


@pytest.fixture
def autorizacao(cliente: TestClient) -> dict[str, str]:
    resposta = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_RESPONSAVEL, "codigo": "123456"}
    )
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_baixa_o_boleto_de_matricula(cliente: TestClient, autorizacao: dict[str, str]) -> None:
    resposta = cliente.get("/api/v1/matriculas/100001/boleto", headers=autorizacao)

    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/pdf"
    assert resposta.content == b"%PDF-1.4 matricula"


def test_nome_do_arquivo_com_espacos_vai_no_content_disposition(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    resposta = cliente.get("/api/v1/matriculas/100001/boleto", headers=autorizacao)

    disposicao = resposta.headers["content-disposition"]
    assert disposicao.startswith("attachment;")
    assert "100001-ANA%20BEATRIZ%20SOUZA%20LIMA.pdf" in disposicao


def test_boleto_de_material_didatico_vem_da_outra_pasta(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    resposta = cliente.get("/api/v1/material-didatico/100001/boleto", headers=autorizacao)

    assert resposta.content == b"%PDF-1.4 material"


def test_aluno_de_outro_responsavel_recebe_403(
    cliente: TestClient, repositorio: RepositorioEmMemoria
) -> None:
    """O JWT carrega as matriculas autorizadas; qualquer outra e barrada."""
    from rematricula.domain.cpf import Cpf
    from rematricula.domain.modelos import Aluno, Responsavel
    from rematricula.domain.telefone import Telefone

    outro = Responsavel(
        ids=("RESP-2",),
        nome="JOAO DA SILVA",
        cpf=Cpf.de_texto(CPF_OUTRO_RESPONSAVEL),
        telefone=Telefone.de_texto("(91) 97777-6666"),
    )
    repositorio.adicionar_responsavel(
        outro, alunos=[Aluno(matricula="300100", nome="PEDRO DA SILVA", turma="3.FD3.2B.T02")]
    )
    token = cliente.post(
        "/api/v1/auth/verificar", json={"cpf": CPF_OUTRO_RESPONSAVEL, "codigo": "123456"}
    ).json()["access_token"]

    resposta = cliente.get(
        "/api/v1/matriculas/100001/boleto", headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "aluno_nao_autorizado"


def test_sem_token_nao_baixa(cliente: TestClient) -> None:
    resposta = cliente.get("/api/v1/matriculas/100001/boleto")

    assert resposta.status_code == 401


def test_boleto_ausente_no_bucket_devolve_404(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    resposta = cliente.get("/api/v1/matriculas/100002/boleto", headers=autorizacao)

    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "boleto_indisponivel"


def test_listagem_marca_quais_boletos_estao_prontos(
    cliente: TestClient, autorizacao: dict[str, str]
) -> None:
    itens = cliente.get("/api/v1/matriculas", headers=autorizacao).json()["itens"]

    disponibilidade = {item["matricula"]: item["boleto_disponivel"] for item in itens}
    assert disponibilidade == {"100001": True, "100002": False}
