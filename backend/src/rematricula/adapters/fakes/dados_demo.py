from datetime import date
from decimal import Decimal

from rematricula.adapters.fakes.armazenamento import ArmazenamentoEmMemoria
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.domain.cpf import Cpf
from rematricula.domain.modelos import Aluno, Responsavel, Servico, Titulo
from rematricula.domain.telefone import Telefone

# CPF de teste canonico: valido no digito verificador, nao pertence a ninguem.
CPF_DEMO = "529.982.247-25"
CODIGO_DEMO = "123456"

_ALUNOS_DEMO = [
    ("100001", "ANA BEATRIZ SOUZA LIMA", "1.FD1.3A.T01"),
    ("100002", "PEDRO HENRIQUE SOUZA LIMA", "2.FD2.1A.T03"),
]


def repositorio_demo() -> RepositorioEmMemoria:
    """Dados ficticios para o front-end integrar antes de o banco estar ligado."""
    repositorio = RepositorioEmMemoria()

    responsavel = Responsavel(
        ids=("1",),
        nome="CARLA SOUZA LIMA",
        cpf=Cpf.de_texto(CPF_DEMO),
        telefone=Telefone.de_texto("(11) 90000-0000"),
    )
    primeiro, segundo = (Aluno(matricula=m, nome=n, turma=t) for m, n, t in _ALUNOS_DEMO)
    repositorio.adicionar_responsavel(responsavel, alunos=[primeiro, segundo])

    valores = [
        (primeiro, Servico.MATRICULA, "1000.00", "800.00"),
        (segundo, Servico.MATRICULA, "1000.00", "800.00"),
        (primeiro, Servico.MATERIAL_DIDATICO, "400.00", "360.00"),
        (segundo, Servico.MATERIAL_DIDATICO, "400.00", "360.00"),
    ]
    for aluno, servico, original, com_desconto in valores:
        repositorio.adicionar_titulo(
            responsavel.ids[0],
            Titulo(
                aluno=aluno,
                servico=servico,
                valor_original=Decimal(original),
                desconto_valido_ate=date(2027, 1, 31),
                valor_com_desconto=Decimal(com_desconto),
            ),
        )

    return repositorio


def armazenamento_demo() -> ArmazenamentoEmMemoria:
    """PDFs de mentira, no mesmo padrao de nome do bucket: {matricula}-{NOME ALUNO}.pdf."""
    armazenamento = ArmazenamentoEmMemoria()

    for servico in (Servico.MATRICULA, Servico.MATERIAL_DIDATICO):
        for matricula, nome, _ in _ALUNOS_DEMO:
            armazenamento.adicionar(
                servico,
                matricula=matricula,
                nome_arquivo=f"{matricula}-{nome}.pdf",
                conteudo=f"%PDF-1.4 boleto de demonstracao {servico} {matricula}".encode(),
            )

    return armazenamento
