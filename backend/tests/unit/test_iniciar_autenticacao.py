import pytest

from rematricula.adapters.fakes.contador import ContadorEmMemoria
from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import ResponsavelNaoEncontrado
from rematricula.use_cases.iniciar_autenticacao import IniciarAutenticacao
from tests.conftest import CPF_RESPONSAVEL, CPF_SEM_CADASTRO


def test_envia_o_codigo_para_o_telefone_cadastrado(
    repositorio: RepositorioEmMemoria, otp: OtpFake
) -> None:
    caso = IniciarAutenticacao(
        repositorio=repositorio, otp=otp, contador=ContadorEmMemoria(), limite_envios=3
    )

    telefone = caso.executar(Cpf.de_texto(CPF_RESPONSAVEL))

    assert telefone.e164 == "+5591988887777"
    assert otp.envios == ["+5591988887777"]


def test_cpf_sem_cadastro_nao_dispara_codigo(
    repositorio: RepositorioEmMemoria, otp: OtpFake
) -> None:
    caso = IniciarAutenticacao(
        repositorio=repositorio, otp=otp, contador=ContadorEmMemoria(), limite_envios=3
    )

    with pytest.raises(ResponsavelNaoEncontrado):
        caso.executar(Cpf.de_texto(CPF_SEM_CADASTRO))

    assert otp.envios == []
