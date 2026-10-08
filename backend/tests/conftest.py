from decimal import Decimal

import pytest

from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.domain.cpf import Cpf
from rematricula.domain.modelos import Aluno, Responsavel, Servico, Titulo
from rematricula.domain.telefone import Telefone

CPF_RESPONSAVEL = "529.982.247-25"
CPF_OUTRO_RESPONSAVEL = "168.995.350-09"
CPF_SEM_CADASTRO = "111.444.777-35"

PRAZO_CAMPANHA = None  # os titulos de teste nao trazem prazo; usa o da campanha


@pytest.fixture
def responsavel() -> Responsavel:
    return Responsavel(
        ids=("RESP-1",),
        nome="CARLA SOUZA LIMA",
        cpf=Cpf.de_texto(CPF_RESPONSAVEL),
        telefone=Telefone.de_texto("(91) 98888-7777"),
    )


@pytest.fixture
def aluno_a() -> Aluno:
    return Aluno(matricula="100001", nome="ANA BEATRIZ SOUZA LIMA", turma="1.FD1.3A.T01")


@pytest.fixture
def aluno_b() -> Aluno:
    return Aluno(matricula="100002", nome="PEDRO HENRIQUE SOUZA LIMA", turma="2.FD2.1A.T03")


@pytest.fixture
def repositorio(responsavel: Responsavel, aluno_a: Aluno, aluno_b: Aluno) -> RepositorioEmMemoria:
    repo = RepositorioEmMemoria()
    repo.adicionar_responsavel(responsavel, alunos=[aluno_a, aluno_b])

    valores = [
        (aluno_a, Servico.MATRICULA, "1000.00", "800.00"),
        (aluno_b, Servico.MATRICULA, "1000.00", "800.00"),
        (aluno_a, Servico.MATERIAL_DIDATICO, "400.00", "360.00"),
    ]
    for aluno, servico, original, com_desconto in valores:
        repo.adicionar_titulo(
            "RESP-1",
            Titulo(
                aluno=aluno,
                servico=servico,
                valor_original=Decimal(original),
                valor_com_desconto=Decimal(com_desconto),
            ),
        )
    return repo


@pytest.fixture
def otp() -> OtpFake:
    return OtpFake(codigo_correto="123456")
