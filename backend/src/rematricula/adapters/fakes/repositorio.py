from collections import defaultdict

from rematricula.domain.cpf import Cpf
from rematricula.domain.modelos import Aluno, Responsavel, Servico, Titulo


class RepositorioEmMemoria:
    """Implementacao de RepositorioMatriculas para testes e desenvolvimento sem credencial."""

    def __init__(self) -> None:
        self._responsaveis: dict[str, Responsavel] = {}
        self._alunos: dict[str, list[Aluno]] = defaultdict(list)
        self._titulos: dict[str, list[Titulo]] = defaultdict(list)

    def adicionar_responsavel(self, responsavel: Responsavel, alunos: list[Aluno]) -> None:
        self._responsaveis[responsavel.cpf.digitos] = responsavel
        for id_responsavel in responsavel.ids:
            self._alunos[id_responsavel] = list(alunos)

    def adicionar_titulo(self, responsavel_id: str, titulo: Titulo) -> None:
        self._titulos[responsavel_id].append(titulo)

    def buscar_responsavel_por_cpf(self, cpf: Cpf) -> Responsavel | None:
        return self._responsaveis.get(cpf.digitos)

    def listar_alunos(self, responsavel_ids: tuple[str, ...]) -> list[Aluno]:
        vistos: dict[str, Aluno] = {}
        for id_responsavel in responsavel_ids:
            for aluno in self._alunos[id_responsavel]:
                vistos.setdefault(aluno.matricula, aluno)
        return list(vistos.values())

    def listar_titulos(self, responsavel_ids: tuple[str, ...], servico: Servico) -> list[Titulo]:
        return [
            titulo
            for id_responsavel in responsavel_ids
            for titulo in self._titulos[id_responsavel]
            if titulo.servico == servico
        ]
