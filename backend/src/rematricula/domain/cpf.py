import hashlib
import re
from dataclasses import dataclass
from typing import Self

from rematricula.domain.erros import CpfInvalido

_NAO_DIGITO = re.compile(r"\D")


def _digito_verificador(digitos: str, peso_inicial: int) -> str:
    soma = sum(int(d) * (peso_inicial - i) for i, d in enumerate(digitos))
    resto = (soma * 10) % 11
    return "0" if resto == 10 else str(resto)


@dataclass(frozen=True, slots=True, repr=False)
class Cpf:
    digitos: str

    @classmethod
    def de_texto(cls, texto: str) -> Self:
        digitos = _NAO_DIGITO.sub("", texto or "")

        if len(digitos) != 11 or len(set(digitos)) == 1:
            raise CpfInvalido("CPF invalido")

        if _digito_verificador(digitos[:9], 10) != digitos[9]:
            raise CpfInvalido("CPF invalido")
        if _digito_verificador(digitos[:10], 11) != digitos[10]:
            raise CpfInvalido("CPF invalido")

        return cls(digitos)

    def mascarado(self) -> str:
        return f"***.***.{self.digitos[6:9]}-{self.digitos[9:]}"

    def hash(self) -> str:
        """Identificador estavel para log e claim de JWT, sem expor o CPF."""
        return hashlib.sha256(self.digitos.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"Cpf({self.mascarado()})"

    def __str__(self) -> str:
        return self.mascarado()
