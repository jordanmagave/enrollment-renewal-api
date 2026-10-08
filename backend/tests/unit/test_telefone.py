import pytest

from rematricula.domain.erros import TelefoneInvalido
from rematricula.domain.telefone import Telefone


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("(91) 98888-7777", "+5591988887777"),
        ("91988887777", "+5591988887777"),
        ("5591988887777", "+5591988887777"),
        ("+55 91 98888-7777", "+5591988887777"),
        ("91 3222-1111", "+559132221111"),  # fixo, 8 digitos
    ],
)
def test_normaliza_para_e164_brasileiro(entrada: str, esperado: str) -> None:
    assert Telefone.de_texto(entrada).e164 == esperado


@pytest.mark.parametrize("entrada", ["", "123", "988887777", "abcdefghijk"])
def test_rejeita_telefone_invalido(entrada: str) -> None:
    with pytest.raises(TelefoneInvalido):
        Telefone.de_texto(entrada)


def test_mascarado_mostra_ddd_e_ultimos_quatro_digitos() -> None:
    assert Telefone.de_texto("(91) 98888-7777").mascarado() == "(91) ****-7777"
