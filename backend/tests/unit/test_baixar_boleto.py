import pytest

from rematricula.adapters.fakes.armazenamento import ArmazenamentoEmMemoria
from rematricula.domain.erros import AlunoNaoAutorizado, BoletoIndisponivel
from rematricula.domain.modelos import Servico, Sessao
from rematricula.use_cases.baixar_boleto import BaixarBoleto

SESSAO = Sessao(responsavel_ids=("RESP-1",), cpf_hash="abc", matriculas=("100001", "100002"))


@pytest.fixture
def armazenamento() -> ArmazenamentoEmMemoria:
    armazenamento = ArmazenamentoEmMemoria()
    armazenamento.adicionar(
        Servico.MATRICULA,
        matricula="100001",
        nome_arquivo="100001-ANA BEATRIZ SOUZA LIMA.pdf",
        conteudo=b"%PDF-1.4 boleto",
    )
    return armazenamento


def test_entrega_o_pdf_do_aluno_autorizado(armazenamento: ArmazenamentoEmMemoria) -> None:
    caso = BaixarBoleto(armazenamento=armazenamento)

    boleto = caso.executar(SESSAO, matricula="100001", servico=Servico.MATRICULA)

    assert boleto.nome_arquivo == "100001-ANA BEATRIZ SOUZA LIMA.pdf"
    assert boleto.conteudo.read() == b"%PDF-1.4 boleto"


def test_recusa_aluno_que_nao_e_do_responsavel(armazenamento: ArmazenamentoEmMemoria) -> None:
    caso = BaixarBoleto(armazenamento=armazenamento)

    with pytest.raises(AlunoNaoAutorizado):
        caso.executar(SESSAO, matricula="999999", servico=Servico.MATRICULA)


def test_aluno_autorizado_sem_arquivo_no_bucket(armazenamento: ArmazenamentoEmMemoria) -> None:
    caso = BaixarBoleto(armazenamento=armazenamento)

    with pytest.raises(BoletoIndisponivel):
        caso.executar(SESSAO, matricula="100002", servico=Servico.MATRICULA)


def test_o_servico_separa_os_arquivos(armazenamento: ArmazenamentoEmMemoria) -> None:
    """Matricula e material didatico moram em pastas diferentes do bucket."""
    caso = BaixarBoleto(armazenamento=armazenamento)

    with pytest.raises(BoletoIndisponivel):
        caso.executar(SESSAO, matricula="100001", servico=Servico.MATERIAL_DIDATICO)
