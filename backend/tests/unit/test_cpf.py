import pytest

from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import CpfInvalido

CPF_VALIDO = "529.982.247-25"


def test_aceita_cpf_formatado_e_guarda_so_digitos() -> None:
    assert Cpf.de_texto(CPF_VALIDO).digitos == "52998224725"


def test_aceita_cpf_sem_formatacao() -> None:
    assert Cpf.de_texto("52998224725").digitos == "52998224725"


def test_ignora_espacos_em_volta() -> None:
    assert Cpf.de_texto("  52998224725  ").digitos == "52998224725"


@pytest.mark.parametrize(
    "entrada",
    [
        "",
        "123",
        "5299822472",  # 10 digitos
        "529982247250",  # 12 digitos
        "abcdefghijk",
        "529.982.247-26",  # digito verificador errado
        "11111111111",  # todos iguais
        "00000000000",
    ],
)
def test_rejeita_cpf_invalido(entrada: str) -> None:
    with pytest.raises(CpfInvalido):
        Cpf.de_texto(entrada)


def test_mascarado_esconde_o_meio() -> None:
    assert Cpf.de_texto(CPF_VALIDO).mascarado() == "***.***.247-25"


def test_hash_e_estavel_e_nao_contem_o_cpf() -> None:
    cpf = Cpf.de_texto(CPF_VALIDO)

    assert cpf.hash() == Cpf.de_texto("52998224725").hash()
    assert "52998224725" not in cpf.hash()


def test_hash_difere_entre_cpfs() -> None:
    assert Cpf.de_texto(CPF_VALIDO).hash() != Cpf.de_texto("168.995.350-09").hash()
