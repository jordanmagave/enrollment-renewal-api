from datetime import date

from rematricula.domain.campanha import Campanha

PRAZO = date(2026, 10, 6)


def test_conta_os_dias_que_faltam_para_o_prazo() -> None:
    campanha = Campanha(desconto_valido_ate=PRAZO)

    assert campanha.dias_restantes(hoje=date(2026, 9, 9)) == 27


def test_ultimo_dia_ainda_conta_como_vigente() -> None:
    campanha = Campanha(desconto_valido_ate=PRAZO)

    assert campanha.dias_restantes(hoje=PRAZO) == 0
    assert campanha.vigente(hoje=PRAZO) is True


def test_depois_do_prazo_o_desconto_expira_e_nao_ha_dias_negativos() -> None:
    campanha = Campanha(desconto_valido_ate=PRAZO)

    assert campanha.vigente(hoje=date(2026, 10, 7)) is False
    assert campanha.dias_restantes(hoje=date(2026, 10, 20)) == 0
