import re
from dataclasses import dataclass
from typing import Self

from rematricula.domain.erros import TelefoneInvalido

_NAO_DIGITO = re.compile(r"\D")
_DDI_BRASIL = "55"


@dataclass(frozen=True, slots=True, repr=False)
class Telefone:
    """Telefone brasileiro em E.164, pronto para o Twilio."""

    e164: str

    @classmethod
    def de_texto(cls, texto: str) -> Self:
        digitos = _NAO_DIGITO.sub("", texto or "")

        if digitos.startswith(_DDI_BRASIL) and len(digitos) in (12, 13):
            digitos = digitos[2:]

        # DDD (2) + numero fixo (8) ou celular (9).
        if len(digitos) not in (10, 11):
            raise TelefoneInvalido("Telefone invalido")

        return cls(f"+{_DDI_BRASIL}{digitos}")

    @property
    def _nacional(self) -> str:
        return self.e164.removeprefix(f"+{_DDI_BRASIL}")

    def mascarado(self) -> str:
        nacional = self._nacional
        return f"({nacional[:2]}) ****-{nacional[-4:]}"

    def __repr__(self) -> str:
        return f"Telefone({self.mascarado()})"

    def __str__(self) -> str:
        return self.mascarado()
