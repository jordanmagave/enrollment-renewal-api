from decimal import Decimal

from rematricula.domain.modelos import Aluno, Servico, Titulo


def aluno() -> Aluno:
    return Aluno(matricula="100001", nome="ANA BEATRIZ SOUZA LIMA", turma="1.FD1.3A.T01")


def test_economia_e_a_diferenca_entre_o_valor_cheio_e_o_com_desconto() -> None:
    titulo = Titulo(
        aluno=aluno(),
        servico=Servico.MATRICULA,
        valor_original=Decimal("1000.00"),
        valor_com_desconto=Decimal("800.00"),
    )

    assert titulo.desconto == Decimal("200.00")


def test_titulo_sem_desconto_tem_economia_zero() -> None:
    titulo = Titulo(
        aluno=aluno(),
        servico=Servico.MATERIAL_DIDATICO,
        valor_original=Decimal("400.00"),
        valor_com_desconto=Decimal("400.00"),
    )

    assert titulo.desconto == Decimal("0.00")
