"""O codigo e derivado, sem estado. O que impede varrer 1 milhao de combinacoes
e o contador de tentativas — por isso ele tem teste proprio."""

import pytest

from rematricula.adapters.fakes.contador import ContadorEmMemoria
from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.adapters.sessao.sessoes_jwt import SessoesJwt
from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import CodigoInvalido, TentativasExcedidas
from rematricula.use_cases.iniciar_autenticacao import IniciarAutenticacao
from rematricula.use_cases.verificar_codigo import VerificarCodigo
from tests.conftest import CPF_RESPONSAVEL, CPF_SEM_CADASTRO

SEGREDO = "segredo-de-teste-com-32-bytes-ou-mais-aqui"


@pytest.fixture
def contador() -> ContadorEmMemoria:
    return ContadorEmMemoria()


def iniciar(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria, limite: int = 3
) -> IniciarAutenticacao:
    return IniciarAutenticacao(
        repositorio=repositorio, otp=otp, contador=contador, limite_envios=limite
    )


def verificar(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria, limite: int = 5
) -> VerificarCodigo:
    return VerificarCodigo(
        repositorio=repositorio,
        otp=otp,
        sessoes=SessoesJwt(segredo=SEGREDO, expira_em_minutos=30),
        contador=contador,
        limite_tentativas=limite,
    )


def test_para_de_enviar_mensagem_depois_do_limite(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    """Cada envio custa dinheiro no WhatsApp; sem limite vira torneira aberta."""
    caso = iniciar(repositorio, otp, contador, limite=3)
    for _ in range(3):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL))

    with pytest.raises(TentativasExcedidas):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL))

    assert len(otp.envios) == 3


def test_bloqueia_apos_o_limite_de_codigos_errados(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    caso = verificar(repositorio, otp, contador, limite=5)
    for _ in range(5):
        with pytest.raises(CodigoInvalido):
            caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")

    with pytest.raises(TentativasExcedidas):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")


def test_bloqueio_vale_mesmo_com_o_codigo_certo(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    """Senao bastaria errar ate acertar."""
    caso = verificar(repositorio, otp, contador, limite=2)
    for _ in range(2):
        with pytest.raises(CodigoInvalido):
            caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")

    with pytest.raises(TentativasExcedidas):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "123456")


def test_acerto_zera_o_contador(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    caso = verificar(repositorio, otp, contador, limite=3)
    with pytest.raises(CodigoInvalido):
        caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")

    caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "123456")

    for _ in range(3):
        with pytest.raises(CodigoInvalido):
            caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "999999")


def test_cpf_sem_cadastro_tambem_consome_tentativa(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    """Sem isso da para varrer CPFs sem gastar tentativa nenhuma."""
    caso = verificar(repositorio, otp, contador, limite=2)
    for _ in range(2):
        with pytest.raises(CodigoInvalido):
            caso.executar(Cpf.de_texto(CPF_SEM_CADASTRO), "123456")

    with pytest.raises(TentativasExcedidas):
        caso.executar(Cpf.de_texto(CPF_SEM_CADASTRO), "123456")


def test_o_bloqueio_de_um_cpf_nao_afeta_outro(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    caso = verificar(repositorio, otp, contador, limite=1)
    with pytest.raises(CodigoInvalido):
        caso.executar(Cpf.de_texto(CPF_SEM_CADASTRO), "999999")

    caso.executar(Cpf.de_texto(CPF_RESPONSAVEL), "123456")


def test_contador_nao_guarda_o_cpf_em_claro(
    repositorio: RepositorioEmMemoria, otp: OtpFake, contador: ContadorEmMemoria
) -> None:
    verificar(repositorio, otp, contador).executar(Cpf.de_texto(CPF_RESPONSAVEL), "123456")

    assert all("52998224725" not in chave for chave in contador.chaves())
