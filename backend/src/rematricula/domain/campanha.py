from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Campanha:
    """Prazo comercial do desconto de rematricula."""

    desconto_valido_ate: date

    def vigente(self, hoje: date) -> bool:
        return hoje <= self.desconto_valido_ate

    def dias_restantes(self, hoje: date) -> int:
        return max(0, (self.desconto_valido_ate - hoje).days)
