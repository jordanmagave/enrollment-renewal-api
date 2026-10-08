from datetime import UTC, datetime, timedelta

import pytest

from rematricula.adapters.otp.codigo_derivado import CodigoDerivado

SEGREDO = "segredo-de-otp-com-32-bytes-ou-mais-aqui"
AGORA = datetime(2026, 9, 10, 14, 30, tzinfo=UTC)
TELEFONE = "+5591988887777"
OUTRO = "+5591977776666"


def gerador(digitos: int = 6, validade: int = 10) -> CodigoDerivado:
    return CodigoDerivado(segredo=SEGREDO, digitos=digitos, validade_minutos=validade)


def test_mesmo_telefone_e_mesma_janela_dao_o_mesmo_codigo() -> None:
    """Nao guardamos o codigo em lugar nenhum: ele e recalculado na conferencia."""
    codigo = gerador().gerar(TELEFONE, agora=AGORA)

    assert gerador().gerar(TELEFONE, agora=AGORA + timedelta(seconds=30)) == codigo


def test_telefones_diferentes_dao_codigos_diferentes() -> None:
    assert gerador().gerar(TELEFONE, agora=AGORA) != gerador().gerar(OUTRO, agora=AGORA)


def test_codigo_tem_o_tamanho_pedido_e_so_digitos() -> None:
    codigo = gerador(digitos=6).gerar(TELEFONE, agora=AGORA)

    assert len(codigo) == 6
    assert codigo.isdigit()


def test_segredo_diferente_muda_o_codigo() -> None:
    outro = CodigoDerivado(
        segredo="outro-segredo-de-32-bytes-ou-mais-aqui", digitos=6, validade_minutos=10
    )

    assert outro.gerar(TELEFONE, agora=AGORA) != gerador().gerar(TELEFONE, agora=AGORA)


def test_confere_o_codigo_da_janela_atual() -> None:
    codigo = gerador().gerar(TELEFONE, agora=AGORA)

    assert gerador().conferir(TELEFONE, codigo, agora=AGORA) is True


def test_aceita_o_codigo_da_janela_anterior() -> None:
    """Sem essa tolerancia, quem recebe o codigo no fim da janela digitaria em vao."""
    antes = AGORA - timedelta(minutes=10)
    codigo = gerador().gerar(TELEFONE, agora=antes)

    assert gerador().conferir(TELEFONE, codigo, agora=AGORA) is True


def test_recusa_codigo_de_duas_janelas_atras() -> None:
    antigo = gerador().gerar(TELEFONE, agora=AGORA - timedelta(minutes=25))

    assert gerador().conferir(TELEFONE, antigo, agora=AGORA) is False


def test_recusa_codigo_de_outro_telefone() -> None:
    codigo = gerador().gerar(OUTRO, agora=AGORA)

    assert gerador().conferir(TELEFONE, codigo, agora=AGORA) is False


@pytest.mark.parametrize("codigo", ["", "12345", "1234567", "abcdef", "  ", "12 34 56"])
def test_recusa_entrada_malformada(codigo: str) -> None:
    assert gerador().conferir(TELEFONE, codigo, agora=AGORA) is False


def test_segredo_curto_e_recusado_na_construcao() -> None:
    with pytest.raises(ValueError, match="32"):
        CodigoDerivado(segredo="curto", digitos=6, validade_minutos=10)
