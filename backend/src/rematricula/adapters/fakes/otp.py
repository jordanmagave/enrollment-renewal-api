from rematricula.domain.telefone import Telefone


class OtpFake:
    """Implementacao de ServicoOtp para testes: aceita um unico codigo e registra os envios."""

    def __init__(self, codigo_correto: str = "123456") -> None:
        self.codigo_correto = codigo_correto
        self.envios: list[str] = []

    def enviar(self, telefone: Telefone) -> None:
        self.envios.append(telefone.e164)

    def verificar(self, telefone: Telefone, codigo: str) -> bool:
        return codigo == self.codigo_correto
