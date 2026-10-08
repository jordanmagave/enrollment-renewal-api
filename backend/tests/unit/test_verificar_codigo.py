import pytest

from rematricula.adapters.fakes.contador import ContadorEmMemoria
from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.adapters.sessao.sessoes_jwt import SessoesJwt
from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import CodigoInvalido
from rematricula.use_cases.verificar_codigo import VerificarCodigo
from tests.conftest import CPF_RESPONSAVEL, CPF_SEM_CADASTRO

SEGREDO = "segredo-de-teste-com-32-bytes-ou-mais-aqui"


def sessoes() -> SessoesJwt:
    return SessoesJwt(segredo=SEGREDO, expira_em_minutos=30)


def caso_de_uso(repositorio: RepositorioEmMemoria, otp: OtpFake) -> VerificarCodigo:
    return VerificarCodigo(
        repositorio=repositorio,
        otp=otp,
        sessoes=sessoes(),
        contador=ContadorEmMemoria(),
        limite_tentativas=5,
    )


def test_codigo_correto_abre_sessao_com_os_alunos_do_responsavel(
    repositorio: RepositorioEmMemoria, otp: OtpFake
) -> None:
    caso = caso_de_uso(repositorio, otp)

    emitido = caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "123456")

    sessao = sessoes().validar(emitido.token)
    assert sessao.responsavel_ids == ("RESP-1",)
    assert sessao.matriculas == ("100001", "100002")
    assert sessao.cpf_hash == Cpf.de_texto(CPF_RESPONSAVEL).hash()


def test_codigo_errado_nao_abre_sessao(repositorio: RepositorioEmMemoria, otp: OtpFake) -> None:
    caso = caso_de_uso(repositorio, otp)

    with pytest.raises(CodigoInvalido):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")


def test_cpf_sem_cadastro_responde_como_codigo_invalido(
    repositorio: RepositorioEmMemoria, otp: OtpFake
) -> None:
    """Nao distingue 'CPF inexistente' de 'codigo errado' — a API nao pode virar
    um oraculo de quem e aluno da escola."""
    caso = caso_de_uso(repositorio, otp)

    with pytest.raises(CodigoInvalido):
        caso.executar(Cpf.de_texto(CPF_SEM_CADASTRO), "123456")
