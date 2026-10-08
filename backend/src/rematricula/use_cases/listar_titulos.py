from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from rematricula.domain.campanha import Campanha
from rematricula.domain.modelos import Servico, Titulo
from rematricula.ports.relogio import Relogio
from rematricula.ports.repositorio import RepositorioMatriculas


@dataclass(frozen=True, slots=True)
class ResumoDeTitulos:
    titulos: list[Titulo]
    ano_letivo: int
    desconto_valido_ate: date
    dias_restantes: int
    desconto_vigente: bool

    @property
    def total_original(self) -> Decimal:
        return sum((t.valor_original for t in self.titulos), Decimal("0"))

    @property
    def total_com_desconto(self) -> Decimal:
        return sum((t.valor_com_desconto for t in self.titulos), Decimal("0"))

    @property
    def economia_total(self) -> Decimal:
        return self.total_original - self.total_com_desconto


@dataclass(frozen=True, slots=True)
class ListarTitulos:
    repositorio: RepositorioMatriculas
    campanha: Campanha
    relogio: Relogio
    ano_letivo: int

    def executar(self, responsavel_ids: tuple[str, ...], servico: Servico) -> ResumoDeTitulos:
        hoje = self.relogio.hoje()
        titulos = self.repositorio.listar_titulos(responsavel_ids, servico)

        # O prazo real vem por titulo do sistema de gestao. O valor de config
        # e so fallback para quando nenhum titulo trouxer data.
        prazos = [t.desconto_valido_ate for t in titulos if t.desconto_valido_ate is not None]
        campanha = Campanha(desconto_valido_ate=min(prazos)) if prazos else self.campanha

        return ResumoDeTitulos(
            titulos=titulos,
            ano_letivo=self.ano_letivo,
            desconto_valido_ate=campanha.desconto_valido_ate,
            dias_restantes=campanha.dias_restantes(hoje),
            desconto_vigente=campanha.vigente(hoje),
        )
