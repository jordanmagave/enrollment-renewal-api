from typing import Protocol

from rematricula.domain.cpf import Cpf
from rematricula.domain.modelos import Aluno, Responsavel, Servico, Titulo


class RepositorioMatriculas(Protocol):
    """Leitura somente-leitura do espelho do sistema de gestao escolar."""

    def buscar_responsavel_por_cpf(self, cpf: Cpf) -> Responsavel | None:
        """None tambem quando o responsavel existe mas nao tem celular utilizavel —
        sem telefone nao ha como enviar o codigo, e a resposta ao cliente e a mesma."""
        ...

    def listar_alunos(self, responsavel_ids: tuple[str, ...]) -> list[Aluno]: ...

    def listar_titulos(self, responsavel_ids: tuple[str, ...], servico: Servico) -> list[Titulo]:
        """Somente titulos em aberto do ano letivo alvo."""
        ...
