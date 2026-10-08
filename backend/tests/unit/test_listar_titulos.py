from datetime import date
from decimal import Decimal

from rematricula.adapters.fakes.relogio import RelogioFixo
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.domain.campanha import Campanha
from rematricula.domain.modelos import Servico
from rematricula.use_cases.listar_titulos import ListarTitulos


def caso_de_uso(repositorio: RepositorioEmMemoria, hoje: date = date(2026, 9, 9)) -> ListarTitulos:
    return ListarTitulos(
        repositorio=repositorio,
        campanha=Campanha(desconto_valido_ate=date(2026, 10, 6)),
        relogio=RelogioFixo(hoje),
        ano_letivo=2027,
    )


def test_lista_os_titulos_de_matricula_do_responsavel(repositorio: RepositorioEmMemoria) -> None:
    resumo = caso_de_uso(repositorio).executar(("RESP-1",), Servico.MATRICULA)

    assert [titulo.aluno.matricula for titulo in resumo.titulos] == ["100001", "100002"]
    assert resumo.total_original == Decimal("2000.00")
    assert resumo.total_com_desconto == Decimal("1600.00")
    assert resumo.economia_total == Decimal("400.00")


def test_material_didatico_traz_so_os_titulos_daquele_servico(
    repositorio: RepositorioEmMemoria,
) -> None:
    resumo = caso_de_uso(repositorio).executar(("RESP-1",), Servico.MATERIAL_DIDATICO)

    assert len(resumo.titulos) == 1
    assert resumo.titulos[0].servico == Servico.MATERIAL_DIDATICO


def test_informa_o_prazo_da_campanha_para_o_front_comunicar_a_urgencia(
    repositorio: RepositorioEmMemoria,
) -> None:
    resumo = caso_de_uso(repositorio, hoje=date(2026, 9, 9)).executar(
        ("RESP-1",), Servico.MATRICULA
    )

    assert resumo.desconto_valido_ate == date(2026, 10, 6)
    assert resumo.dias_restantes == 27
    assert resumo.desconto_vigente is True


def test_depois_do_prazo_a_campanha_aparece_como_encerrada(
    repositorio: RepositorioEmMemoria,
) -> None:
    resumo = caso_de_uso(repositorio, hoje=date(2026, 10, 7)).executar(
        ("RESP-1",), Servico.MATRICULA
    )

    assert resumo.desconto_vigente is False
    assert resumo.dias_restantes == 0


def test_responsavel_sem_titulo_recebe_lista_vazia_e_totais_zerados(
    repositorio: RepositorioEmMemoria,
) -> None:
    resumo = caso_de_uso(repositorio).executar(("RESP-SEM-NADA",), Servico.MATRICULA)

    assert resumo.titulos == []
    assert resumo.total_com_desconto == Decimal("0")
    assert resumo.economia_total == Decimal("0")
